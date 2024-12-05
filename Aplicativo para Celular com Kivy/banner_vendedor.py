from botoes import ImageButton, LabelButton
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import  Rectangle, Color
import requests
from kivy.app import  App
from functools import partial


class BannerVendedor(FloatLayout):

    def __init__(self, **kwargs):
        super().__init__()
        

        with self.canvas:
            Color(rgb=(0, 0, 0, 1))
            self.rec = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.atualizar_rec, size=self.atualizar_rec)

        id_vendedor = kwargs["id_vendedor"]


        link = f'https://aplicativovendahash-db98e-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"&equalTo="{id_vendedor}"'
        requisicao = requests.get(link)
        requisicao_dict = requisicao.json()
        valores = list(requisicao_dict.values())[0]
        avatar = valores['avatar']
        total_vendas = valores['total_vendas']

        meu_app = App.get_running_app()

        imagem = ImageButton(source=f"icones/fotos_perfil/{avatar}", 
                             pos_hint = {"right": 0.4, "top": 0.9}, size_hint = (0.3, 0.8), on_release=partial(meu_app.carregar_vendasvendedor, valores))
        label_id = LabelButton(text=f"ID Vendedor: {id_vendedor}", 
                               pos_hint = {"right": 0.9, "top": 0.9}, size_hint = (0.5, 0.5), on_release=partial(meu_app.carregar_vendasvendedor, valores))
        label_total = LabelButton(text=f"Total de Vendas: R${total_vendas}", 
                                  pos_hint = {"right": 0.9, "top": 0.6}, size_hint = (0.5, 0.5), on_release=partial(meu_app.carregar_vendasvendedor, valores))

        self.add_widget(imagem)
        self.add_widget(label_id)
        self.add_widget(label_total)


    def atualizar_rec(self, *args):
        self.rec.pos = self.pos
        self.rec.size = self.size
