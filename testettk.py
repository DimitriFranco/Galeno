import math
import customtkinter
from tkinter import filedialog
from PIL import Image
import parsifal_to_zotero_2
import threading as th


def alerta_filtragem(janela_pai):

    resposta = {"valor": None}

    alerta = customtkinter.CTkToplevel(janela_pai)
    alerta.title("Filtragem")
    alerta.geometry("320x160")
    alerta.resizable(False, False)
    alerta.transient(janela_pai)  
    alerta.grab_set()       
    texto = customtkinter.CTkLabel(alerta, text="Deseja aplicar a filtragem de artigos aceitos?", wraplength=280, justify="center")
    texto.pack(pady=20)
    frame_botoes = customtkinter.CTkFrame(alerta, fg_color="transparent")
    frame_botoes.pack(pady=10)

    def sim():
        resposta["valor"] = True
        alerta.destroy()

    def nao():
        resposta["valor"] = False
        alerta.destroy()

    botao_sim = customtkinter.CTkButton(frame_botoes, text="Sim", width=100, command=sim)
    botao_sim.pack(side="left", padx=10)
    botao_nao = customtkinter.CTkButton(frame_botoes, text="Não", width=100, fg_color="#444444", command=nao)
    botao_nao.pack(side="left", padx=10)
    janela_pai.wait_window(alerta)
    return resposta["valor"]


class SegmentedButton(customtkinter.CTkFrame):
    def __init__(self, master, values, command=None):
        super().__init__(master)

        self.command = command
        self.value = None
        self.buttons = {}

        self.grid_columnconfigure((0, 1), weight=1)

        for i, val in enumerate(values):
            btn = customtkinter.CTkButton(
                self,
                text=val,
                fg_color="transparent",
                border_width=2,
                border_color="#FBBF24",
                text_color="#FBBF24",
                hover_color="#2A2A2A",
                command=lambda v=val: self.select(v)
            )
            btn.grid(row=0, column=i, padx=8, pady=10, sticky="ew")
            self.buttons[val] = btn

        self.select(values[0])

    def select(self, value):
        self.value = value

        for val, btn in self.buttons.items():
            if val == value:
                btn.configure(
                    fg_color="#FBBF24",
                    text_color="black",
                    border_width=0
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color="#FBBF24",
                    border_width=2
                )

        if self.command:
            self.command(value)

    def get(self):
        return self.value


class MyCheckboxFrame(customtkinter.CTkFrame):
    def __init__(self, master, title, values):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.values = values
        self.title = title
        self.checkboxes = []

        self.title = customtkinter.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        for i, value in enumerate(self.values):
            checkbox = customtkinter.CTkCheckBox(self, text=value)
            checkbox.grid(row=i+1, column=0, padx=10, pady=(10, 0), sticky="w")
            self.checkboxes.append(checkbox)

    def get(self):
        checked_checkboxes = []
        for checkbox in self.checkboxes:
            if checkbox.get() == 1:
                checked_checkboxes.append(checkbox.cget("text"))
        return checked_checkboxes
    
class MyRadiobuttonFrame(customtkinter.CTkFrame):
    def __init__(self, master, title, values, command=None):
            super().__init__(master)
            self.grid_columnconfigure(0, weight=1)
            self.values = values
            self.title = title
            self.command = command
            self.radiobuttons = []
            self.variable = customtkinter.StringVar(value="")

            self.title = customtkinter.CTkLabel(self, text=self.title, fg_color="transparent", font=("Arial", 20))
            self.title.grid(row=0, column=0, padx=25, pady=(10, 0), sticky="w")

            for i, value in enumerate(self.values): 
                radiobutton = customtkinter.CTkRadioButton(self, text=value, value=value, variable=self.variable, command=self.command, fg_color="#FBBF24")
                radiobutton.grid(row=1, column=i, padx=20, pady=20, sticky="w")
                self.radiobuttons.append(radiobutton)

    def get(self):
            return self.variable.get()

    def set(self, value):
            self.variable.set(value)
            


class MyEntryFrame(customtkinter.CTkFrame):
    def __init__(self, master, title, placeholder=""):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.title_text = title
        self.variable = customtkinter.StringVar()

        self.title = customtkinter.CTkLabel(self, text=self.title_text)
        self.title.grid(row=0, column=0, padx=10, sticky="w")

        self.entry = customtkinter.CTkEntry(self, textvariable=self.variable, placeholder_text=placeholder)
        self.entry.grid(row=1, column=0, padx=10, pady=(0,10), sticky="ew")

    def get(self):
        return self.variable.get()

    def set(self, value):
        self.variable.set(value)




class Plato_App(customtkinter.CTk):

    def __init__(self):
        super().__init__()

        self.title("Galeno")
        self.geometry("1400x830")
        self.resizable(False, False)
        #self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0,1), weight=1)

        #-----------------------BARRA MENU-------------------------------------------------------------
        self.frame_top_menu = customtkinter.CTkFrame(self)
        self.frame_top_menu.grid(row=0, column=0, padx=0, pady=0, sticky="new", columnspan=2)
        self.frame_top_menu.columnconfigure(3, weight=1)

        self.img_logo = customtkinter.CTkImage(light_image=Image.open("galeno_icon.png"), size=(40, 40))
        self.label_logo = customtkinter.CTkLabel(self.frame_top_menu, text="", image=self.img_logo)
        self.label_logo.grid(row=0, column=0, padx=(20, 0), pady=20)

        self.nome = customtkinter.CTkLabel(self.frame_top_menu, text="GALENO", text_color="#FBBF24", font=("Arial", 20))
        self.nome.grid(row=0, column=1, padx=20, pady=20, sticky="w")
        
        self.descricao = customtkinter.CTkLabel(self.frame_top_menu, text="|  Parsifal X Zotero ", text_color="#A1A1A1", font=("Arial", 12))
        self.descricao.grid(row=0, column=2, padx=0, pady=20, sticky="w")

        self.version = customtkinter.CTkLabel(self.frame_top_menu, text="")
        self.version.grid(row=0, column=3, padx=20, pady=20, sticky="e")

        #-----------------------BARRA MENU-------------------------------------------------------------

        self.divider = customtkinter.CTkFrame(self,height=2, fg_color="#FBBF24")
        self.divider.grid(row=1, column=0, columnspan=99, sticky="ew",padx=20, pady=0)

        #---------------------ZOTERO CONFIGURACAO---------------------------------------------------------
        self.frame_zotero_login = customtkinter.CTkFrame(self, fg_color="#1A1A1A")
        self.frame_zotero_login.grid_columnconfigure(0, weight=1)
        self.frame_zotero_login.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

        self.zotero_configuracao = customtkinter.CTkLabel(self.frame_zotero_login, text="Configuração Zotero", fg_color="transparent", corner_radius=6)
        self.zotero_configuracao.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")

        self.user_id = MyEntryFrame(self.frame_zotero_login, "ID do Usuário", "Digite seu ID")
        self.user_id.grid(row=2, column=0, padx=10, pady=10, sticky="ew", columnspan=2)

        def botao_selecionado(valor):
            if valor == "Individual": 
                self.user_id.title.configure(text="ID do Usuário")
            else:
                self.user_id.title.configure(text="ID do Grupo")
        self.caixa_selecao = SegmentedButton(self.frame_zotero_login, values=["Individual", "Grupo"], command=botao_selecionado) 
        self.caixa_selecao.grid(row=1, column=0, sticky="ew", padx=10, columnspan=2)
 
        self.zotero_id = MyEntryFrame(self.frame_zotero_login, "Zotero API Key", "Digite o ID de sua biblioteca")
        self.zotero_id.grid(row=3, column=0, padx=10, pady=10, sticky="ew", columnspan=2)
        self.url_ativa = None
        self.key_ativa = None
        def confirmar_id():
            id_user = self.user_id.get() 
            api_key = self.zotero_id.get()
            tipo = self.caixa_selecao.get()
            conexao, url, key = parsifal_to_zotero_2.login_zotero(id_user, api_key, tipo)
            if conexao:
                self.conexao_status.configure(text="CONECTADO")
                self.conexao_bola.configure(image=self.conectado_icon)
                self.key_ativa = key
                self.url_ativa = url
            return None
        self.botao_confirma = customtkinter.CTkButton(self.frame_zotero_login, text="Confirmar", command=confirmar_id, fg_color="#FBBF24", hover_color="#E9B42F", text_color="#1A1A1A", border_width=1, border_color="#2A2A2A", corner_radius=8, height=25)
        self.botao_confirma.grid(row=4, column=1, padx=10, pady=(0,10), sticky="e")

        self.frame_conexao = customtkinter.CTkFrame(self.frame_zotero_login, fg_color="transparent")
        self.frame_conexao.grid(row=4, column=0, padx=20, pady=(0,10), sticky="w")

        self.conectado_icon = customtkinter.CTkImage(light_image=Image.open("conectado.png"), size=(20,20))
        self.desconectado_icon = customtkinter.CTkImage(light_image=Image.open("desconectado.png"), size=(15, 15))
        self.conexao_bola = customtkinter.CTkLabel(self.frame_conexao, text="", image=self.desconectado_icon)
        self.conexao_bola.grid(row=0, column=0, padx=15)

        self.conexao_status = customtkinter.CTkLabel(self.frame_conexao, text="DESCONECTADO")
        self.conexao_status.grid(row=0, column=1)
        #---------------------ZOTERO CONFIGURACAO---------------------------------------------------------

        #----------------------CARREGAR O ARQUIVO--------------------------------------------------------
        self.frame_carregar_arquivo = customtkinter.CTkFrame(self, fg_color="#1A1A1A")
        self.frame_carregar_arquivo.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        self.frame_carregar_arquivo.grid_columnconfigure(0, weight=1)

        self.zotero_carregar = customtkinter.CTkLabel(self.frame_carregar_arquivo, text="Carregar arquivo CSV:")
        self.zotero_carregar.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.frame_area_arquivo = customtkinter.CTkFrame(self.frame_carregar_arquivo, fg_color="#1D1D1D")
        self.frame_area_arquivo.grid(row=1, column=0, padx=70, pady=(0, 20), sticky="nsew")
        self.frame_area_arquivo.grid_columnconfigure(0, weight=1)

        self.img_carregar = customtkinter.CTkImage(light_image=Image.open("carregar_icon.png"), size=(50,50))
        self.label_img_carregar = customtkinter.CTkLabel(self.frame_area_arquivo, text="", image=self.img_carregar)
        self.label_img_carregar.grid(row=0, column=0, pady=(70, 0))

        self.texto_carregar = customtkinter.CTkLabel(self.frame_area_arquivo, text="Selecione um arquivo CSV para ser carregado e executado.")
        self.texto_carregar.grid(row=1, column=0, pady=(10, 20))


        def carregar_arquivo():
            caminho = filedialog.askopenfilename(title="Selecionar arquivo CSV", filetypes=[("Arquivos CSV", "*.csv")])
            if caminho:
                parsifal_to_zotero_2.leitura_csv(caminho)
                print("Arquivo selecionado:", caminho)
                self.frame_aviso_carregado.lift()
                fazer = alerta_filtragem(self)
                aceitos = parsifal_to_zotero_2.filtragem(fazer, caminho) 
                tempo_calc = math.ceil((len(aceitos) * 1.17))
                tempo_estimado = f': {tempo_calc} segundos.' 
                self.frame_artigos_carregados.lift()
                self.aviso_carregado.configure(text=f'Aguarde enquanto carregamos seus artigos... \n ATENÇÃO: Isso pode demorar alguns minutos.\n Tempo Estimado{tempo_estimado}')
                self.update_idletasks()
                parsifal_to_zotero_2.enviar_artigos(aceitos, caminho, self.url_ativa, self.key_ativa, self.add_artigo)
                self.aviso_carregado.configure(text="CONCLUÍDO")
        
        thread = th.Thread(target=carregar_arquivo)

        def carregar_arquivo_th():
            thread.start()

        self.button_carregar = customtkinter.CTkButton(self.frame_area_arquivo, text="Carregar Arquivo", command=carregar_arquivo_th, fg_color="#FBBF24", text_color="#000000")
        self.button_carregar.grid(row=2, column=0, pady=(0, 70))
        #----------------------CARREGAR O ARQUIVO--------------------------------------------------------
        
        self.frame_aviso_carregado = customtkinter.CTkFrame(self.frame_area_arquivo, fg_color="#1D1D1D")
        self.frame_aviso_carregado.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.frame_aviso_carregado.lower()
        #tempo_estimado = "Carregando..."
        self.aviso_carregado = customtkinter.CTkLabel(self.frame_aviso_carregado, text=f'Aguarde enquanto carregamos seus artigos... \n ATENÇÃO: Isso pode demorar alguns minutos.')
        self.aviso_carregado.place(relx=0.5, rely=0.5, anchor="center")

        #------------------------ARTIGOS CARREGADOS-------------------------------------------------------
        self.frame_artigos = customtkinter.CTkFrame(self)
        self.frame_artigos.grid(row=2, column=1, padx=20, pady=10, rowspan=2, sticky="nsew")
        self.frame_artigos.grid_columnconfigure(0, weight=1)
        self.frame_artigos.grid_rowconfigure(0, weight=1)

        self.texto_artigos = customtkinter.CTkLabel(self.frame_artigos, text="Os artigos carregados aparecerão aqui.")
        self.texto_artigos.grid(row=0, column=0, sticky="nsew")

        self.frame_artigos_carregados = customtkinter.CTkScrollableFrame(self)
        self.frame_artigos_carregados.grid(row=2, column=1, padx=20, pady=10, rowspan=2, sticky="nsew")
        self.frame_artigos.grid_columnconfigure(0, weight=1)
        self.frame_artigos.grid_rowconfigure(0, weight=1)
        self.frame_artigos_carregados.lower()

    def add_artigo(self, title):
        customtkinter.CTkLabel(self.frame_artigos_carregados, text=title, anchor="w").pack(fill="x", padx=10, pady=4)




app = Plato_App()  
app.mainloop()