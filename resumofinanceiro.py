import pdfplumber
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import os
import subprocess
import psycopg2

def conectar_bd():
    conn = psycopg2.connect(
        host="pontomais.postgresql.dbaas.com.br",
        user="pontomais",
        password="tsc10012000@",
        database="pontomais",
        port=5432
    )
    return conn

def verificar_pdf_cadastrado(pdf_texto):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT texto FROM financeiroresumo WHERE texto = %s", (pdf_texto,))
    result = cursor.fetchone()
    cursor.close()  # Feche o cursor após a consulta
    conn.close()
    return result

def cadastrar_pdf(pdf_texto):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO financeiroresumo (texto) VALUES (%s)", (pdf_texto,))
    conn.commit()
    cursor.close()  
    conn.close()

def extrair_texto(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        page = pdf.pages[-1]
        width = page.width
        height = page.height
        area = (width - 300, height - 405, width, height - 200)
        texto = page.within_bbox(area).extract_text()
    return texto

def exibir_resumo_negocios(pdf_file):
    texto = extrair_texto(pdf_file)
    
    result = verificar_pdf_cadastrado(texto)
    if result:
        pdf_texto_db = result[0]
        if texto not in pdf_texto_db:
            pdf_texto_db += "\n" + texto
            conn = conectar_bd()
            cursor = conn.cursor()
            cursor.execute("UPDATE financeiroresumo SET texto = %s WHERE texto = %s", (pdf_texto_db, texto))
            conn.commit()
            cursor.close()  
            conn.close()
        texto += "\n\n(PDF já cadastrado no banco de dados)"
    else:
        cadastrar_pdf(texto)
    
    root_resumo = tk.Tk()
    root_resumo.title("Resumo de Negócios")
    root_resumo.configure(bg='orange')
    
    texto_label = tk.Label(root_resumo, text=texto, font=("Arial", 10), anchor="w", justify="left", wraplength=500)
    texto_label.pack(padx=10, pady=5)

    button_voltar_inicio = tk.Button(root_resumo, text="Voltar ao Início", command=voltar_inicio, font=("Arial", 12), bg='light blue')
    button_voltar_inicio.pack(side="left", padx=10, pady=10)
    
    root_resumo.mainloop()

def on_canvas_configure(event):
    canvas_links.configure(scrollregion=canvas_links.bbox("all"))

def selecionar_pasta():
    folder_path = filedialog.askdirectory()
    if folder_path:
        pdfs_paths = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
        
        contador_label.config(text=f"Número de PDFs: {len(pdfs_paths)}")
        
        progress_bar['maximum'] = len(pdfs_paths)
        progress_bar['value'] = 0
        
        for widget in frame_buttons.winfo_children():
            widget.destroy()
        
        for pdf_path in pdfs_paths:
            button = tk.Button(frame_buttons, text=pdf_path, command=lambda path=os.path.join(folder_path, pdf_path): exibir_resumo_negocios(path), bg='light blue')
            button.pack(side="top", padx=5, pady=5)
            progress_bar['value'] += 1
            root.update_idletasks()

        canvas_links.update_idletasks()
        
        cadastrar_pdfs_na_pasta(folder_path)

def voltar_inicio():
    root.destroy()
    subprocess.Popen(['python', 'folha.py'])

def cadastrar_pdfs_na_pasta(folder_path):
    pdfs_paths = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
    for pdf_path in pdfs_paths:
        texto = extrair_texto(os.path.join(folder_path, pdf_path))
        result = verificar_pdf_cadastrado(texto)
        if not result:
            cadastrar_pdf(texto)

root = tk.Tk()
root.title("Extrair Texto")
root.configure(bg='orange')

button_selecionar_pasta = tk.Button(root, text="Selecionar Pasta com PDFs", command=selecionar_pasta, font=("Arial", 12), bg='light blue')
button_selecionar_pasta.pack(pady=10)

contador_label = tk.Label(root, text="Número de PDFs: 0", bg='orange', font=("Arial", 12))
contador_label.pack(pady=5)

canvas_links = tk.Canvas(root, bg='orange')
canvas_links.pack(side="left", fill="both", expand=True)

scrollbar_links = ttk.Scrollbar(root, orient="vertical", command=canvas_links.yview)
scrollbar_links.pack(side="right", fill="y")

frame_buttons = tk.Frame(canvas_links, bg='orange')
frame_buttons.bind("<Configure>", on_canvas_configure)

canvas_links.create_window((0, 0), window=frame_buttons, anchor='nw')
canvas_links.configure(yscrollcommand=scrollbar_links.set)

button_voltar_inicio = tk.Button(root, text="Voltar ao Início", command=voltar_inicio, font=("Arial", 12), bg='light blue')
button_voltar_inicio.pack(side="left", padx=10, pady=10)


progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10, anchor='s')

root.mainloop()

