import tkinter as tk
from tkinter import filedialog
import PyPDF2
import re 
import os

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
            if match_data_pregao:
                data_pregao = match_data_pregao.group(1)
        
        return nr_nota, data_pregao

def exibir_info(folder_path):
    file_list = os.listdir(folder_path)
    info_text = ""
    for file_name in file_list:
        if file_name.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, file_name)
            nr_nota, data_pregao = extrair_informacoes(pdf_path)
            if nr_nota and data_pregao:
                info_text += f"Nr. nota: {nr_nota}\nData pregão: {data_pregao}\n\n"
            else:
                info_text += "Nr. nota: Informação não encontrada\nData pregão: Informação não encontrada\n\n"
    
    info_label.config(text=info_text)

def selecionar_pasta():
    folder_path = filedialog.askdirectory()
    if folder_path:
        exibir_info(folder_path)

root = tk.Tk()
root.title("Extrair informações do PDF")
root.configure(bg='yellow')

info_label = tk.Label(root, text="", bg='yellow')
info_label.pack()

button_selecionar_pasta = tk.Button(root, text="Selecionar pasta com PDFs", command=selecionar_pasta, bg='navy', fg='white')
button_selecionar_pasta.pack()

root.mainloop()
