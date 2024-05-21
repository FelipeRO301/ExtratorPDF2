import tkinter as tk
from tkinter import filedialog, ttk
import psycopg2
import PyPDF2
import re
import os
import subprocess

def conectar_bd():
    return psycopg2.connect(
        host="pontomais.postgresql.dbaas.com.br",
        user="pontomais",
        password="tsc10012000@",
        database="pontomais",
        port=5432
    )

def verificar_pdf_cadastrado(nr_nota):
    conn = conectar_bd()
    cursor = conn.cursor()
    
    cursor.execute("SELECT 1 FROM informacoes WHERE nr_nota = %s", (nr_nota,))
    result = cursor.fetchone()
    
    conn.close()
    
    print("PDF cadastrado?", result)  
    
    return result is not None

def cadastrar_pdf(nr_nota, data_pregao):
    conn = conectar_bd()
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO informacoes (nr_nota, data_pregao) VALUES (%s, %s)", (nr_nota, data_pregao))
    
    conn.commit()
    conn.close()

    print("PDF cadastrado com sucesso:", nr_nota, data_pregao)  

def extrair_informacoes(pdf_file):
    with open(pdf_file, 'rb') as file:
        reader = PyPDF2.PdfReader(file)

        nr_nota = None
        data_pregao = None

        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text = page.extract_text()

            match_nr_nota = re.search(r'Nr\. nota\s*([\d]+)', text)
            match_data_pregao = re.search(r'Data pregão\s*(\d{2}/\d{2}/\d{4})', text)

            if match_nr_nota:
                nr_nota = match_nr_nota.group(1)
                print("Nr. nota:", nr_nota)  
            if match_data_pregao:
                data_pregao = match_data_pregao.group(1)
                print("Data pregão:", data_pregao)

       
                if not verificar_pdf_cadastrado(nr_nota):
                    cadastrar_pdf(nr_nota, data_pregao)

        return nr_nota, data_pregao
    
def exibir_info(folder_path):
    file_list = os.listdir(folder_path)
    info_text = ""
    pdf_count = 0 

    progress_bar['maximum'] = len(file_list)
    progress_bar['value'] = 0

    for file_name in file_list:
        if file_name.endswith(".pdf"):
            pdf_count += 1  
            pdf_path = os.path.join(folder_path, file_name)
            nr_nota, data_pregao = extrair_informacoes(pdf_path)
            texto = f"Nr. nota: {nr_nota}\nData pregão: {data_pregao}\n\n"
            info_text += texto
            
         
            progress_bar['value'] += 1
            root.update_idletasks()

    info_label.config(text=info_text)
    contador_label.config(text=f"Número de PDFs: {pdf_count}")  # Atualiza a label do contador

def selecionar_pasta():
    folder_path = filedialog.askdirectory()
    if folder_path:
        exibir_info(folder_path)

def abrir_negociosrealizados():
    subprocess.Popen(['python', 'negociosrealizados.py'])

def abrir_resumofinanceiro():
    subprocess.Popen(['python', 'resumofinanceiro.py'])

def abrir_resumonegocios():
    subprocess.Popen(['python', 'resumonegocios.py'])

root = tk.Tk()
root.title("Extrair informações do PDF")
root.configure(bg='yellow')

frame_left = tk.Frame(root, bg='yellow')
frame_left.pack(side='left', padx=10, pady=10)

frame_right = tk.Frame(root, bg='yellow')
frame_right.pack(side='right', padx=10, pady=10)

canvas = tk.Canvas(frame_right, bg='yellow')
canvas.pack(side="left", fill="both", expand=True)

scrollbar = tk.Scrollbar(frame_right, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")

canvas.configure(yscrollcommand=scrollbar.set)

canvas_frame = tk.Frame(canvas, bg='yellow')
canvas.create_window((0, 0), window=canvas_frame, anchor='nw')

info_label = tk.Label(canvas_frame, text="", bg='yellow')
info_label.pack()

canvas_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=canvas_frame, anchor="nw")

canvas.configure(yscrollcommand=scrollbar.set, scrollregion=canvas.bbox("all"))

button_selecionar_pasta = tk.Button(frame_left, text="Selecionar pasta com PDFs", command=selecionar_pasta, bg='navy', fg='white')
button_selecionar_pasta.pack(pady=10)

button_negociosrealizados = tk.Button(frame_left, text="Negócios Realizados", command=abrir_negociosrealizados, bg='navy', fg='white')
button_negociosrealizados.pack(pady=10)

button_resumofinanceiro = tk.Button(frame_left, text="Resumo Financeiro", command=abrir_resumofinanceiro, bg='navy', fg='white')
button_resumofinanceiro.pack(pady=10)

button_resumonegocios = tk.Button(frame_left, text="Resumo Negócios", command=abrir_resumonegocios, bg='navy', fg='white')
button_resumonegocios.pack(pady=10)

contador_label = tk.Label(root, text="Número de PDFs: 0", bg='yellow', font=('Arial', 14))
contador_label.pack(pady=10)


progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10)

root.mainloop()
