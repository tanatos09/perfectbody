import os

# Cesta k adresáři projektu (můžete ji upravit podle svého projektu)
project_path = "C:\Users\info\Documents\Python-SDA\perfectbody"  # Např. "C:/Users/Username/PycharmProjects/MyProject"

# Seznam pro ukládání nalezených souborů
file_list = []

# Procházení adresářů
for root, dirs, files in os.walk(project_path):
    for file in files:
        if file.endswith(".html") or file.endswith(".css"):
            file_list.append(os.path.join(root, file))

# Vytisknutí všech nalezených souborů
print("Nalezené soubory:")
for file in file_list:
    print(file)


output_file = "seznam_souboru.txt"

# Uložení seznamu do souboru
with open(output_file, "w", encoding="utf-8") as f:
    for file in file_list:
        f.write(file + "\n")

print(f"Seznam souborů byl uložen do: {output_file}")
