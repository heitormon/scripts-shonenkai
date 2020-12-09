import pandas
import argparse
import requests
import time
import io
#"Carimbo de data/hora","Nome de usuário","email","É a primeira vez que está participando?","nome","RG","Data de nascimento","Idade","Sexo","Igreja ou Casa de divulgação","Regional","rua","numero","complemento","bairro","cidade","uf","cep","Nome da mãe ou responsável","Nome do pai ou responsável","Número de celular com DDD","Número de telefone fixo com DDD","Autorização de imagem","Autorização de participação",""
# Alterar a header (primeira linha do arquivo) do csv


def get_inscricoes(file):
    s=requests.get(file)
    print('READING FILE',s.text)
    # list_inscricoes = pandas.read_csv(file, sep=',', encoding='utf-8')
    list_inscricoes = pandas.read_csv(io.StringIO(s.text))
    print('CSV LEN BEFORE DUPLICATE FILTER: ' + str(len(list_inscricoes)))
    # list_inscricoes = list_inscricoes.drop_duplicates()
    # print('CSV LEN AFTER DUPLICATE FILTER: ' + str(len(list_inscricoes)))
    return list_inscricoes


def prepare_validation(list_inscricoes):
    inscricoes = []
    for inscricao in list_inscricoes.itertuples():
        rua = inscricao.rua
        numero = inscricao.numero
        bairro = inscricao.bairro
        cidade = inscricao.cidade
        uf = inscricao.uf
        cep = inscricao.cep
        nome = inscricao.nome
        inscricoes.append({
            "nome": nome,
            "numero": numero,
            "bairro": bairro,
            "cidade": cidade,
            "uf": uf,
            "rua": rua,
            "cep": cep
        })
    return inscricoes


def validate_address(list_endereco):
    list_error = []
    i = 0
    for endereco in list_endereco:
        enederecos_viacep = send_viacep(endereco)
        print(i)
        if len(enederecos_viacep) == 0:
            list_error.append({
                "endereco": endereco,
                "error": "Endereço não encontrado"
            })
        else:
            if endereco["cep"] in enederecos_viacep != True:
                list_error.append({
                    "endereco": endereco,
                    "error": f"CEP não condizente"
                })
        i += 1
    return list_error


def send_viacep(endereco):
    url = f'https://viacep.com.br/ws/{endereco["uf"]}/{endereco["cidade"]}/{endereco["rua"]}/json/'
    response = requests.get(url)
    return [i["cep"] for i in response.json()]


if __name__ == '__main__':
    start_time = time.time()
    parser = argparse.ArgumentParser(prog='main')
    parser.add_argument('-f', '--file', help='Users file', required=True)
    args = parser.parse_args()
    print('Caminho do arquivo: ', args.file)
    list_inscricoes = get_inscricoes(args.file)
    list_inscricoes = prepare_validation(list_inscricoes)
    print('Lista Sanitizada: ', list_inscricoes)
    list_error = validate_address(list_inscricoes)
    print('Erros no endereco', list_error)
    print("--- %s seconds ---" % (time.time() - start_time))

