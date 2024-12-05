from kivy.app import App
from kivy.lang import Builder
from telas import *
from botoes import *
import requests
from banner_venda import *
import os
import certifi
from functools import partial
from myfirebase import *
from banner_vendedor import *
from datetime import date
import json


os.environ["SSL_CERT_FILE"] = certifi.where()


GUI = Builder.load_file("main.kv")
class MainApp(App):
    cliente = None
    produto = None
    unidade = None

    def build(self):
        self.firebase = MyFirebase()
        return GUI
    
    def on_start(self):


        arquivos = os.listdir('icones/fotos_perfil')
        pagina_fotoperfil = self.root.ids["fotoperfilpage"]
        lista_fotos = pagina_fotoperfil.ids['lista_fotos_perfil']
        for foto in arquivos:
            imagem = ImageButton(source=f'icones/fotos_perfil/{foto}', on_release=partial(self.mudar_foto_perfil, foto))
            lista_fotos.add_widget(imagem)

        arquivos = os.listdir('icones/fotos_clientes')
        pagina_adicionarvenda = self.root.ids["adicionarvendaspage"]
        lista_cliente = pagina_adicionarvenda.ids['lista_clientes']
        for foto_cliente in arquivos:
            imagem = ImageButton(source=f"icones/fotos_clientes/{foto_cliente}", on_release=partial(self.selecionar_cliente, foto_cliente))
            label = LabelButton(text=foto_cliente.replace(".png", "").capitalize(), on_release=partial(self.selecionar_cliente, foto_cliente))
            lista_cliente.add_widget(imagem)
            lista_cliente.add_widget(label)

        arquivos = os.listdir('icones/fotos_produtos')
        pagina_adicionarvenda_produto = self.root.ids["adicionarvendaspage"]
        lista_produto = pagina_adicionarvenda_produto.ids['lista_produtos']
        for foto_produto in arquivos:
            imagem = ImageButton(source=f"icones/fotos_produtos/{foto_produto}", on_release=partial(self.selecionar_produto, foto_produto))
            label = LabelButton(text=foto_produto.replace(".png", "").capitalize(), on_release=partial(self.selecionar_produto, foto_produto))
            lista_produto.add_widget(imagem)
            lista_produto.add_widget(label)

        pagina_adicionarvenda_data = self.root.ids["adicionarvendaspage"]
        pagina_adicionarvenda_data.ids["label_data"].text = f"Data: {date.today().strftime('%d/%m/%Y')}"

        



        self.carregar_infos_usuarios()
        

    def carregar_infos_usuarios(self):
        try:
            with open("refreshtoken.txt", "r") as arquivo:
                refresh_token = arquivo.read()

            local_id, id_token = self.firebase.trocar_token(refresh_token)
            self.local_id = local_id
            self.id_token = id_token

            requisicao = requests.get(f'https://aplicativovendahash-db98e-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}')
            requisicao_dict = requisicao.json()

            avatar = requisicao_dict['avatar']
            self.avatar = avatar
            foto_perfil = self.root.ids["foto_perfil"]
            foto_perfil.source = f'icones/fotos_perfil/{avatar}'

            id_vendedor = requisicao_dict['id_vendedor']
            self.id_vendedor = id_vendedor
            pagina_ajustepage = self.root.ids["ajustepage"]
            pagina_ajustepage.ids["id_vendedor"].text = f'Seu ID único: {id_vendedor}'

            total_vendas = requisicao_dict['total_vendas']
            self.total_vendas = total_vendas
            homepage = self.root.ids["homepage"]
            homepage.ids["label_total_vendas"].text = f'[color=#000000]Total de Vendas: [/color][b]R${total_vendas}[/b]'

            self.equipe = requisicao_dict['equipe']



            try:
                vendas = requisicao_dict['vendas']
                self.vendas = vendas
                pagina_homepage = self.root.ids['homepage']
                lista_vendas = pagina_homepage.ids['lista_vendas']

                for id_venda in vendas:
                    venda = vendas[id_venda]
                    banner = BannerVenda(cliente=venda['cliente'], foto_cliente=venda['foto_cliente'],
                                        produto=venda['produto'], foto_produto=venda['foto_produto'],
                                        data=venda['data'], preco=venda['preco'],
                                        unidade=venda['unidade'], quantidade=venda['quantidade'])
                    
                    lista_vendas.add_widget(banner)
            except:
                pass

            equipe = requisicao_dict['equipe']
            lista_equipe = equipe.split(",")
            pagina_listavendedores = self.root.ids["listarvendedorespage"]
            lista_vendedores = pagina_listavendedores.ids["lista_vendedores"]
            
            for id_vendedor_equipe in lista_equipe:
                if id_vendedor_equipe != "":
                    banner_vendedor = BannerVendedor(id_vendedor=id_vendedor_equipe)
                    lista_vendedores.add_widget(banner_vendedor)


            self.mudar_tela("homepage")

        except:
            pass
    
    def mudar_tela(self, id_tela):
        gereicador_telas = self.root.ids["screen_manager"]
        gereicador_telas.current = id_tela

    def mudar_foto_perfil(self, foto, *args):
        foto_perfil = self.root.ids["foto_perfil"]
        foto_perfil.source = f'icones/fotos_perfil/{foto}'

        info = f'{{"avatar" : "{foto}"}}'
        requisicao = requests.patch(f'https://aplicativovendahash-db98e-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}', data=str(info))

        self.mudar_tela("ajustepage")

    def adicionar_vendedor(self, id_vendedor_adicionado):
        link = f'https://aplicativovendahash-db98e-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"&equalTo="{id_vendedor_adicionado}"'
        requisicao = requests.get(link)
        requisicao_dict = requisicao.json()

        pagina_adicionarvendedor = self.root.ids['adicionarvendedorpage']
        mensagem_texto = pagina_adicionarvendedor.ids['mensagem_outrovendedor']

        if requisicao_dict == {}:
            mensagem_texto.text = "Usuário não encontrado!"
        else:
            equipe = self.equipe.split(",")
            if id_vendedor_adicionado in equipe:
                mensagem_texto.text = "Vendedor já faz parte da equipe!"
            else:
                self.equipe = self.equipe + f",{id_vendedor_adicionado}"
                info = f'{{"equipe" : "{self.equipe}"}}'
                requests.patch(f'https://aplicativovendahash-db98e-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}', data=info)
                mensagem_texto.text = "Vendedor Adicionado com Sucesso"
                pagina_listavendedores = self.root.ids["listarvendedorespage"]
                lista_vendedores = pagina_listavendedores.ids["lista_vendedores"]
                banner_vendedor = BannerVendedor(id_vendedor=id_vendedor_adicionado)
                lista_vendedores.add_widget(banner_vendedor)
        
    def selecionar_cliente(self, foto, *args):
        self.cliente = foto.replace(".png", "")
        pagina_adicionarvenda = self.root.ids["adicionarvendaspage"]
        lista_cliente = pagina_adicionarvenda.ids['lista_clientes']

        for item in list(lista_cliente.children):
            item.color = (1, 1, 1, 1)
            try:
                texto = item.text.lower() + ".png"
                if foto == texto:
                    item.color = (0, 207/255, 219/255, 1)
                    item.canvas.ask_update()
            except:
                pass

    def selecionar_produto(self, foto, *args ):
        self.produto = foto.replace(".png", "")
        pagina_adicionarvenda_produto = self.root.ids["adicionarvendaspage"]
        lista_produto = pagina_adicionarvenda_produto.ids['lista_produtos']

        for item in list(lista_produto.children):
            item.color = (1, 1, 1, 1)
            try:
                texto = item.text.lower() + ".png"
                if foto == texto:
                    item.color = (0, 207/255, 219/255, 1)
                    item.canvas.ask_update()
            except:
                pass

    def selecionar_unidade(self, id_label, *args):
        self.unidade = id_label.replace("unidades_", "")
        pagina_adicionarvenda_unidades = self.root.ids["adicionarvendaspage"]
        pagina_adicionarvenda_unidades.ids["unidades_kg"].color = (1, 1, 1, 1)
        pagina_adicionarvenda_unidades.ids["unidades_unidades"].color = (1, 1, 1, 1)
        pagina_adicionarvenda_unidades.ids["unidades_litros"].color = (1, 1, 1, 1)


        pagina_adicionarvenda_unidades.ids[id_label].color = (0, 207/255, 219/255, 1)

    def adicionar_vendas(self):
        cliente = self.cliente
        produto = self.produto
        unidade = self.unidade
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        data = pagina_adicionarvendas.ids["label_data"].text.replace("Data: ", "")
        preco = pagina_adicionarvendas.ids["preco_total"].text
        quantidade = pagina_adicionarvendas.ids["quantidade"].text

        if not cliente:
            pagina_adicionarvendas.ids["selecione_cliente"].color = (1, 0, 0, 1)
        if not produto:
            pagina_adicionarvendas.ids["selecione_produto"].color = (1, 0, 0, 1)
        if not unidade:
            pagina_adicionarvendas.ids["unidades_kg"].color = (1, 0, 0, 1)
            pagina_adicionarvendas.ids["unidades_unidades"].color = (1, 0, 0, 1)
            pagina_adicionarvendas.ids["unidades_litros"].color = (1, 0, 0, 1)
        if not preco:
            pagina_adicionarvendas.ids["selecione_preco"].color = (1, 0, 0, 1)
        else:
            try:
                preco = float(preco)
            except:
                pagina_adicionarvendas.ids["selecione_preco"].color = (1, 0, 0, 1)
        if not quantidade:
            pagina_adicionarvendas.ids["selecione_quantidade"].color = (1, 0, 0, 1)
        else:
            try:
                quantidade = float(quantidade)
            except:
                pagina_adicionarvendas.ids["selecione_quantidade"].color = (1, 0, 0, 1)

        if cliente and produto and unidade and preco and quantidade and (type(preco) == float) and (type(quantidade) == float):
            foto_produto = produto + ".png"
            foto_cliente = cliente + ".png"

            info = {
                "cliente": cliente,
                "produto": produto,
                "foto_cliente": foto_cliente,
                "foto_produto": foto_produto,
                "data": data,
                "unidade": unidade,
                "preco": preco,
                "quantidade": quantidade
            }
            try:
                response = requests.post(
                    f'https://aplicativovendahash-db98e-default-rtdb.firebaseio.com/{self.local_id}/vendas.json?auth={self.id_token}',
                    data=json.dumps(info)
                )
                if response.status_code == 200:
                    print("Venda adicionada com sucesso!")
                    # Resetar os campos visuais
                    pagina_adicionarvendas.ids["preco_total"].text = ""
                    pagina_adicionarvendas.ids["quantidade"].text = ""
                    self.cliente = None
                    self.produto = None
                    self.unidade = None
                    self.mudar_tela("homepage")
                else:
                    print("Erro ao adicionar venda:", response.text)
            except Exception as e:
                print(f"Erro na conexão: {e}")
            try:
                banner = BannerVenda(cliente=cliente, produto=produto, 
                                    foto_cliente=foto_cliente, foto_produto=foto_produto, 
                                    data=data, preco=preco, quantidade=quantidade, unidade=unidade)
                pagina_homepage = self.root.ids['homepage']
                lista_vendas = pagina_homepage.ids['lista_vendas']
                lista_vendas.add_widget(banner)
                print("Banner adicionado com Sucesso !")
            except Exception as e:
                print(f"Erro ao acionar o Banner: {e}")

            try:
                requisicao = requests.get(f'https://aplicativovendahash-db98e-default-rtdb.firebaseio.com/{self.local_id}/total_vendas.json?auth={self.id_token}')
                total_vendas = float(requisicao.json())
                total_vendas += preco
                info = {"total_vendas" : total_vendas}
            
                response = requests.patch(f'https://aplicativovendahash-db98e-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}', data=json.dumps(info))
                if response.status_code == 200:
                    print("Preço total das vendas alterado com Sucesso")
                    homepage = self.root.ids["homepage"]
                    homepage.ids["label_total_vendas"].text = f'[color=#000000]Total de Vendas: [/color][b]R${total_vendas}[/b]'
                else:
                    print(f"Erro ao atualizar total de vendas: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Erro ao atualizar total de vendas: {e}")
        else:
            print("Erro: Todos os campos obrigatórios devem ser preenchidos corretamente.")

    def carregar_todasvendas(self):
        pagina_todasvendas = self.root.ids["todasvendaspage"]
        lista_vendas = pagina_todasvendas.ids["lista_vendas"]

        for item in list(lista_vendas.children):
            lista_vendas.remove_widget(item)

        requisicao = requests.get(f'https://aplicativovendahash-db98e-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"')
        requisicao_dict = requisicao.json()

        foto_perfil = self.root.ids["foto_perfil"]
        foto_perfil.source = f'icones/fotos_perfil/hash.png'
        

        total_vendas = 0

        for local_id_usuario in requisicao_dict:
            try:
                vendas = requisicao_dict[local_id_usuario]["vendas"]
                for id_venda in vendas:
                    venda = vendas[id_venda]
                    total_vendas += float(venda["preco"])
                    banner = BannerVenda(cliente=venda["cliente"], produto=venda["produto"], 
                                foto_cliente=venda["foto_cliente"], foto_produto=venda["foto_produto"], 
                                data=venda["data"], preco=venda["preco"], quantidade=venda["quantidade"], unidade=venda["unidade"])
                    lista_vendas.add_widget(banner)
            except Exception as e:
                print(f"Erro: {e}")
        

            pagina_todasvendas.ids["label_total_vendas"].text = f'[color=#000000]Total de Vendas: [/color][b]R${total_vendas}[/b]'

            self.mudar_tela("todasvendaspage")

    def sair_todas_vendas(self, id_tela):
        foto_perfil = self.root.ids["foto_perfil"]
        foto_perfil.source = f'icones/fotos_perfil/{self.avatar}'

        self.mudar_tela(id_tela)

    def carregar_vendasvendedor(self, dict_info_vendedor, *args):
        
        
        try:
            pagina_vendasoutrovendedor = self.root.ids["vendasoutrosvendedorpage"]
            lista_vendas = pagina_vendasoutrovendedor.ids["lista_vendas"]
            vendas = dict_info_vendedor["vendas"]


            for item in list(lista_vendas.children):
                lista_vendas.remove_widget(item)


            for id_venda in vendas:
                venda = vendas[id_venda]
                banner = BannerVenda(cliente=venda["cliente"], produto=venda["produto"], 
                            foto_cliente=venda["foto_cliente"], foto_produto=venda["foto_produto"], 
                            data=venda["data"], preco=venda["preco"], quantidade=venda["quantidade"], unidade=venda["unidade"])
                lista_vendas.add_widget(banner)
        except Exception as e:
            print(f"Erro: {e}")
        
        total_vendas = dict_info_vendedor["total_vendas"]
        pagina_vendasoutrovendedor.ids["label_total_vendas"].text = f'[color=#000000]Total de Vendas: [/color][b]R${total_vendas}[/b]'

        foto_perfil = self.root.ids["foto_perfil"]
        foto_perfil.source = f'icones/fotos_perfil/{dict_info_vendedor["avatar"]}'



        self.mudar_tela("vendasoutrosvendedorpage")

    
MainApp().run()
