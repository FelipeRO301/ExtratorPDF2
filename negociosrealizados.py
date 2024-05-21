import os
import re
import tkinter as tk
from tkinter import filedialog, ttk
from tkinter import Button 
import pdfplumber
import subprocess
import psycopg2

def conectar_bd():
    return psycopg2.connect(
        host="pontomais.postgresql.dbaas.com.br",
        user="pontomais",
        password="tsc10012000@",
        database="pontomais",
        port=5432
    )

def criar_tabela_negociacoes():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS negociacoes (
            id SERIAL PRIMARY KEY,
            tipo VARCHAR(10),
            especificacao VARCHAR(100),
            quantidade INT,
            preco_ajuste FLOAT
        )
    """)
    conn.commit()
    conn.close()

def extrair_negocios(pdf_file):
    negocios = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            matches = re.finditer(r'(C|V)\s+(.*?)\s+(\d+)\s+([\d,]+)', text)
            for match in matches:
                tipo = match.group(1)
                especificacao = match.group(2)
                quantidade = match.group(3)
                preco_ajuste = match.group(4).replace(',', '.') 
                negocios.append((tipo, especificacao, quantidade, preco_ajuste))
    return negocios

def exibir_tabela(pdf_file):
    frame_links.grid_forget()
    frame_tabela.pack(fill="both", expand=True)
    negocios = extrair_negocios(pdf_file)
    
    for row in treeview.get_children():
        treeview.delete(row)

    for i, negocio in enumerate(negocios, start=1):
        treeview.insert("", "end", text=str(i), values=negocio)
    
    if not verificar_dados_existentes(negocios):
        print("Cadastrando dados na tabela negociacoes...")
        cadastrar_negociacoes(negocios)
        print("Dados cadastrados na tabela negociacoes com sucesso!")
    else:
        print("Os dados já foram cadastrados anteriormente.")

def verificar_dados_existentes(negocios):
    conn = conectar_bd()
    cursor = conn.cursor()
    for negocio in negocios:
        cursor.execute("SELECT * FROM negociacoes WHERE tipo = %s AND especificacao = %s AND quantidade = %s AND preco_ajuste = %s", negocio)
        if cursor.fetchone():
            conn.close()
            return True
    conn.close()
    return False

def cadastrar_negociacoes(negocios):
    conn = conectar_bd()
    cursor = conn.cursor()
    for negocio in negocios:
        cursor.execute("INSERT INTO negociacoes (tipo, especificacao, quantidade, preco_ajuste) VALUES (%s, %s, %s, %s)", negocio)
    conn.commit()
    conn.close()

def selecionar_pasta():
    folder_path = filedialog.askdirectory()
    if folder_path:
        print("Pasta selecionada:", folder_path)
        pdfs_paths = [os.path.join(folder_path, file_name) for file_name in os.listdir(folder_path) if file_name.endswith(".pdf")]
        
        contador_label.config(text=f"Número de PDFs: {len(pdfs_paths)}")
        
        progress_bar['maximum'] = len(pdfs_paths)
        progress_bar['value'] = 0

        for widget in frame_buttons.winfo_children():
            widget.destroy()
        for pdf_path in pdfs_paths:
            button = tk.Button(frame_buttons, text=pdf_path, command=lambda path=pdf_path: exibir_tabela(path), bg='light blue')
            button.grid(sticky="ew")
            progress_bar['value'] += 1
            root.update_idletasks()
    canvas_links.update_idletasks() 
    canvas_links.config(scrollregion=canvas_links.bbox("all"))

def voltar_links():
    frame_tabela.pack_forget()
    frame_links.pack(fill="both", expand=True)

def voltar_inicio():
    root.destroy()
    subprocess.Popen(['python', 'folha.py'])

root = tk.Tk()
root.title("Dados dos Negócios")
root.configure(bg='orange')

frame_links = tk.Frame(root, bg='orange')
frame_links.pack(fill="both", expand=True)

canvas_links = tk.Canvas(frame_links, bg='orange')
canvas_links.pack(side="left", fill="both", expand=True)

scrollbar_links = tk.Scrollbar(frame_links, orient="vertical", command=canvas_links.yview)
scrollbar_links.pack(side="right", fill="y")

canvas_links.configure(yscrollcommand=scrollbar_links.set)
scrollbar_links.config(command=canvas_links.yview)

frame_buttons = tk.Frame(canvas_links, bg='orange')
canvas_links.create_window((0, 0), window=frame_buttons, anchor='nw')

canvas_links.bind_all("<MouseWheel>", lambda event: canvas_links.yview_scroll(int(-1*(event.delta/120)), "units"))

button_selecionar_pasta = tk.Button(frame_links, text="Selecionar pasta com PDFs", command=selecionar_pasta, bg='light blue')
button_selecionar_pasta.pack(fill="x")

frame_tabela = tk.Frame(root, bg='orange')

treeview = ttk.Treeview(frame_tabela)
treeview["columns"] = ("Tipo", "Especificação do Título", "Quantidade", "Preço / Ajuste")

treeview.heading("#0", text="Índice")
treeview.column("#0", width=50)

for column in treeview["columns"]:
    treeview.heading(column, text=column)
    treeview.column(column, width=150)

frame_tabela_botoes = tk.Frame(frame_tabela, bg='orange')
frame_tabela_botoes.pack(pady=10)

Button(frame_tabela_botoes, text="Voltar para links", command=voltar_links, bg='light blue').pack()
Button(frame_tabela_botoes, text="Voltar ao Início", command=voltar_inicio, bg='light blue').pack()

treeview.pack(fill="both", expand=True)

info_label = tk.Label(frame_links, text="", bg='orange')
info_label.pack()

contador_label = tk.Label(frame_links, text="Número de PDFs: 0", bg='orange', font=('Arial', 14))
contador_label.pack(pady=10, anchor='e')


progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10, anchor='s')

criar_tabela_negociacoes()
root.mainloop()
