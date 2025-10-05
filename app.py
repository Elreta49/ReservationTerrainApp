import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.filedialog import asksaveasfilename
import csv
import os
from tkcalendar import DateEntry
from fpdf import FPDF
import datetime
import tempfile
import win32api
import win32print


# ========== Fonctions ==========

def enregistrer():
    global selected_item
    nom = entry_nom.get()
    type_demandeur = entry_type_demandeur.get()
    terrain = entry_terrain.get()
    date = entry_date.get()
    heure_debut = entry_heure_debut.get()
    heure_fin = entry_heure_fin.get()

    # Heure fin doit être après heure début
    try:
        h_debut, _ = map(int, heure_debut.split(":"))
        h_fin, _ = map(int, heure_fin.split(":"))
        if h_fin <= h_debut:
            messagebox.showerror("Erreur", "L'heure de fin doit être après l'heure de début.")
            selected_item = None
            return
    except:
        pass

    duree = entry_duree.get()
    telephone = entry_telephone.get()
    montant = entry_montant.get()
    etat_paiement = entry_etat_paiement.get()

    if not nom or not date:
        messagebox.showwarning("Champ vide", "Merci de remplir au moins le nom et la date.")
        selected_item = None
        return

    # Vérifier si l'heure début ou fin est déjà réservée pour la date ET le terrain choisis
    fichier = "reservations.csv"
    if os.path.exists(fichier):
        with open(fichier, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if len(row) >= 7 and row[3] == terrain and row[4] == date:
                    # Si on est en modification, ignorer la ligne qu'on modifie
                    if selected_item:
                        ancienne_valeurs = tableau.item(selected_item)["values"]
                        numero = ancienne_valeurs[0]
                        if row[0] == str(numero):
                            continue
                    if row[5] == heure_debut:
                        messagebox.showerror("Erreur", f"L'heure début {heure_debut} est déjà réservée pour ce terrain et cette date.")
                        return
                    if row[6] == heure_fin:
                        messagebox.showerror("Erreur", f"L'heure fin {heureFin} est déjà réservée pour ce terrain et cette date.")
                        return

    # Vérifier qu'il n'y a pas de chevauchement pour le même terrain et la même date
    fichier = "reservations.csv"
    if os.path.exists(fichier):
        with open(fichier, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if len(row) >= 7 and row[3] == terrain and row[4] == date:
                    # Récupère les heures déjà réservées
                    h_deb_exist, _ = map(int, row[5].split(":"))
                    h_fin_exist, _ = map(int, row[6].split(":"))
                    # Nouvelles heures
                    h_deb_new, _ = map(int, heure_debut.split(":"))
                    h_fin_new, _ = map(int, heure_fin.split(":"))
                    # Test de chevauchement
                    if (h_deb_new < h_fin_exist and h_fin_new > h_deb_exist):
                        messagebox.showerror(
                            "Erreur",
                            f"Conflit avec une réservation existante de {row[5]} à {row[6]} sur ce terrain."
                        )
                        return

    valeurs = (
        nom, type_demandeur, terrain, date,
        heure_debut, heure_fin, duree, telephone, montant, etat_paiement
    )

    fichier = "reservations.csv"
    if selected_item:
        ancienne_valeurs = tableau.item(selected_item)["values"]
        numero = ancienne_valeurs[0]
        # Toujours ajouter " DH" même si l'utilisateur a tapé juste le chiffre
        montant_affiche = montant.strip()
        if not montant_affiche.endswith("DH"):
            montant_affiche = f"{montant_affiche} DH"
        valeurs = (
            numero, nom, type_demandeur, terrain, date,
            heure_debut, heure_fin, duree, telephone,
            montant_affiche,
            etat_paiement
        )
        tableau.item(selected_item, values=valeurs)
        # Correction ici :
        lignes = []
        with open(fichier, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            entete = next(reader)
            lignes.append(entete)
            for row in reader:
                if str(row[0]) == str(numero):
                    lignes.append(list(valeurs))
                else:
                    lignes.append(row)
        with open(fichier, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(lignes)
        selected_item = None
    else:
        numero = get_next_ref()
        montant_affiche = montant.strip()
        if not montant_affiche.endswith("DH"):
            montant_affiche = f"{montant_affiche} DH"
        valeurs = (
            numero, nom, type_demandeur, terrain, date,
            heure_debut, heure_fin, duree, telephone,
            montant_affiche,
            etat_paiement
        )
        fichier_existe = os.path.exists(fichier)
        with open(fichier, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not fichier_existe:
                writer.writerow([
                    "N°", "Nom", "Type de demandeur", "Terrain demandé", "Date",
                    "Heure début", "Heure fin", "Durée", "Téléphone", "Montant", "État de paiement"
                ])
            writer.writerow(valeurs)
            tableau.insert("", "end", values=valeurs)

    # Reset les champs
    entry_nom.delete(0, tk.END)
    entry_type_demandeur.set("")
    entry_terrain.set("")
    entry_date.set_date(datetime.date.today())
    entry_heure_debut.set("")
    entry_heure_fin.set("")
    entry_duree.delete(0, tk.END)
    entry_telephone.delete(0, tk.END)
    entry_montant.set("")
    entry_etat_paiement.set("")

    afficher_total_montant()  # <-- Ajouté ici

def charger_tableau():
    if not os.path.exists("reservations.csv"):
        return
    with open("reservations.csv", mode='r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if len(row) == 11:
                tableau.insert("", "end", values=tuple(row))

def supprimer():
    selected = tableau.selection()
    if not selected:
        messagebox.showwarning("Aucune sélection", "Sélectionnez une réservation à supprimer.")
        return

    ligne = tableau.item(selected[0])["values"]

    confirm = messagebox.askyesno("Confirmer", f"Supprimer la réservation de {ligne[1]} du {ligne[4]} ?")
    if not confirm:
        return

    tableau.delete(selected[0])

    # Lire toutes les lignes du CSV
    lignes_restantes = []
    with open("reservations.csv", mode='r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        entete = next(reader)
        lignes_restantes.append(entete)
        for row in reader:
            # Compare uniquement le numéro de réservation (colonne 0)
            if str(row[0]) != str(ligne[0]):
                lignes_restantes.append(row)

    # Réécrire le CSV sans la ligne supprimée
    with open("reservations.csv", mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(lignes_restantes)
        f.flush()

    afficher_total_montant()  # <-- Ajouté ici

    messagebox.showinfo("Supprimée", "Réservation supprimée avec succès ✅")

def rechercher():
    search_term = entry_search.get().lower()
    for item in tableau.get_children():
        tableau.delete(item)

    if not os.path.exists("reservations.csv"):
        return

    with open("reservations.csv", mode='r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        entete = next(reader, None)
        idx = 1
        for row in reader:
            # Recherche sur le nom (colonne 0)
            if search_term in row[0].lower():
                if len(row) == 8:
                    # Affiche dans le même ordre que le tableau (N°, Nom, Type de demandeur, Téléphone, Date, Heure, Durée, Terrain demandé, Remarque)
                    tableau.insert(
                        "", "end",
                        values=(idx, row[0], row[1], row[2], row[3], row[4], row[5], row[6, row[7]])
                    )
                    idx += 1

def champ(label, parent):
    tk.Label(parent, text=label, bg="white").pack(anchor="w", pady=(0,2))
    entry = tk.Entry(parent, width=28, bg="#f6f6f6", relief="flat", highlightthickness=1, highlightbackground="#cccccc")
    entry.pack(pady=(0,8))
    return entry

def remplir_formulaire_depuis_selection():
    global selected_item
    selected = tableau.selection()
    if not selected:
        messagebox.showwarning("Aucune sélection", "Sélectionnez une réservation à modifier.")
        return
    selected_item = selected[0]
    valeurs = tableau.item(selected_item)["values"]
    # valeurs = (N°, Nom, Type de demandeur, Terrain demandé, Date, Heure début, Heure fin, Durée, Téléphone, Montant, État de paiement)

    # Nom
    entry_nom.delete(0, tk.END)
    entry_nom.insert(0, valeurs[1])

    # Type de demandeur
    if valeurs[2] in entry_type_demandeur["values"]:
        entry_type_demandeur.set(valeurs[2])
    else:
        entry_type_demandeur.set("")

    # Terrain demandé
    if valeurs[3] in entry_terrain["values"]:
        entry_terrain.set(valeurs[3])
    else:
        entry_terrain.set("")

    # Date
    try:
        entry_date.set_date(valeurs[4])
    except Exception:
        entry_date.set_date(datetime.date.today())

    # Heure début
    if valeurs[5] in entry_heure_debut["values"]:
        entry_heure_debut.set(valeurs[5])
    else:
        entry_heure_debut.set("")

    # Heure fin
    if valeurs[6] in entry_heure_fin["values"]:
        entry_heure_fin.set(valeurs[6])
    else:
        entry_heure_fin.set("")

    # Durée (readonly)
    entry_duree.config(state="normal")
    entry_duree.delete(0, tk.END)
    entry_duree.insert(0, valeurs[7])
    entry_duree.config(state="readonly")

    # Téléphone
    entry_telephone.delete(0, tk.END)
    entry_telephone.insert(0, valeurs[8])

    # Montant
    montant_val = valeurs[9].replace("DH", "").replace("dh", "").strip()
    if montant_val in entry_montant["values"]:
        entry_montant.set(montant_val)
    else:
        entry_montant["values"] = (*entry_montant["values"], montant_val)
        entry_montant.set(montant_val)

    # État de paiement
    if valeurs[10] in entry_etat_paiement["values"]:
        entry_etat_paiement.set(valeurs[10])
    else:
        entry_etat_paiement.set("")


def imprimer_pdf():
    selected = tableau.selection()
    if not selected:
        messagebox.showwarning("Aucune sélection", "Sélectionnez une réservation à imprimer.")
        return

    valeurs = tableau.item(selected[0])["values"]
    # valeurs = (N°, Nom, Type de demandeur, Terrain demandé, Date, Heure début, Heure fin, Durée, Téléphone, Montant, État de paiement)

    from fpdf import FPDF
    from tkinter.filedialog import asksaveasfilename

    nom_pdf = f"recu_reservation_{valeurs[0]}.pdf"
    file_path = asksaveasfilename(
        defaultextension=".pdf",
        initialfile=nom_pdf,
        filetypes=[("PDF files", "*.pdf")],
        title="Enregistrer le reçu PDF sous..."
    )
    if not file_path:
        return

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Largeur totale du tableau (col1 + col2)
    col1, col2 = 55, 60
    table_width = col1 + col2

    # Centre le titre
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 12, "REÇU DE RÉSERVATION", ln=True, align="C")
    pdf.ln(6)

    # Calcule la marge pour centrer le tableau
    page_width = pdf.w - 2 * pdf.l_margin
    x_table = (page_width - table_width) / 2 + pdf.l_margin

    # Tableau des infos (numéro inclus)
    champs = [
        ("Numéro de réservation", valeurs[0]),
        ("Nom du Réservataire", valeurs[1]),
        ("Type de demandeur", valeurs[2]),
        ("Terrain demandé", valeurs[3]),
        ("Date de réservation", valeurs[4]),
        ("Heure début", valeurs[5]),
        ("Heure fin", valeurs[6]),
        ("Durée", valeurs[7]),
        ("Téléphone", valeurs[8]),
        ("Montant", valeurs[9]),
        ("État de paiement", valeurs[10]),
    ]

    pdf.set_font("Arial", "B", 11)
    pdf.set_fill_color(255, 255, 255)
    for label, value in champs:
        pdf.set_x(x_table)
        pdf.cell(col1, 9, label, border=1)
        pdf.set_font("Arial", "", 11)
        pdf.cell(col2, 9, str(value), border=1, ln=True)
        pdf.set_font("Arial", "B", 11)

    pdf.ln(8)
    # Centre le texte de remerciement sous le tableau
    pdf.set_font("Arial", "I", 10)
    pdf.set_x(x_table)
    pdf.cell(table_width, 8, "Merci pour votre réservation.", ln=True, align="C")

    pdf.output(file_path)

def imprimer_direct():
    selected = tableau.selection()
    if not selected:
        messagebox.showwarning("Aucune sélection", "Sélectionnez une réservation à imprimer.")
        return

    valeurs = tableau.item(selected[0])["values"]

    # Génère un PDF temporaire
    from fpdf import FPDF
    import os
    import tempfile

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 12, "REÇU DE RÉSERVATION", ln=True, align="C")
    pdf.ln(6)
    col1, col2 = 55, 60
    table_width = col1 + col2
    page_width = pdf.w - 2 * pdf.l_margin
    x_table = (page_width - table_width) / 2 + pdf.l_margin
    champs = [
        ("Numéro de réservation", valeurs[0]),
        ("Nom du Réservataire", valeurs[1]),
        ("Type de demandeur", valeurs[2]),
        ("Terrain demandé", valeurs[3]),
        ("Date de réservation", valeurs[4]),
        ("Heure début", valeurs[5]),
        ("Heure fin", valeurs[6]),
        ("Durée", valeurs[7]),
        ("Téléphone", valeurs[8]),
        ("Montant", valeurs[9]),
        ("État de paiement", valeurs[10]),
    ]
    pdf.set_font("Arial", "B", 11)
    for label, value in champs:
        pdf.set_x(x_table)
        pdf.cell(col1, 9, label, border=1)
        pdf.set_font("Arial", "", 11)
        pdf.cell(col2, 9, str(value), border=1, ln=True)
        pdf.set_font("Arial", "B", 11)
    pdf.ln(8)
    pdf.set_font("Arial", "I", 10)
    pdf.set_x(x_table)
    pdf.cell(table_width, 8, "Merci pour votre réservation.", ln=True, align="C")

    # Sauvegarde dans un fichier temporaire
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp.name)
    temp.close()

    # Ouvre le PDF avec le lecteur PDF par défaut (Edge, Adobe, etc.)
    os.startfile(temp.name)

def get_next_ref():
    refs = []
    for item in tableau.get_children():
        ref = tableau.item(item)["values"][0]
        if isinstance(ref, str) and ref.startswith("BM"):
            try:
                refs.append(int(ref[2:]))
            except:
                pass
    if refs:
        return f"BM{max(refs)+1}"
    else:
        return "BM1"

def calculer_duree(event=None):
    debut = entry_heure_debut.get()
    fin = entry_heure_fin.get()
    entry_duree.config(state="normal")
    entry_duree.delete(0, tk.END)
    if debut and fin:
        try:
            h_debut, m_debut = map(int, debut.split(":"))
            h_fin, m_fin = map(int, fin.split(":"))
            t_debut = h_debut + m_debut/60
            t_fin = h_fin + m_fin/60
            duree = t_fin - t_debut
            if duree > 0:
                if duree.is_integer():
                    entry_duree.insert(0, f"{int(duree)}h")
                else:
                    entry_duree.insert(0, f"{duree:.1f}h")
            # sinon, ne rien mettre
        except:
            pass
    entry_duree.config(state="readonly")

def update_heures_disponibles(event=None):
    date_choisie = entry_date.get()
    heures_occupees = set()
    if os.path.exists("reservations.csv"):
        with open("reservations.csv", mode='r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if len(row) >= 7 and row[4] == date_choisie:
                    heures_occupees.add(row[5])
                    heures_occupees.add(row[6])  # Ajoute aussi l'heure fin occupée

    # Toujours afficher toutes les heures
    entry_heure_debut['values'] = heures_debut
    entry_heure_fin['values'] = heures_debut

    # Si une heure est déjà réservée, la vider si sélectionnée
    if entry_heure_debut.get() in heures_occupees:
        entry_heure_debut.set("")
    if entry_heure_fin.get() in heures_occupees:
        entry_heure_fin.set("")

def colorer_heure_debut(event=None):
    heure = entry_heure_debut.get()
    date_choisie = entry_date.get()
    heures_occupees = set()
    if os.path.exists("reservations.csv"):
        with open("reservations.csv", mode='r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if len(row) >= 7 and row[4] == date_choisie:
                    heures_occupees.add(row[5])
    if heure in heures_occupees:
        entry_heure_debut.configure(foreground="red")
    elif heure:
        entry_heure_debut.configure(foreground="green")
    else:
        entry_heure_debut.configure(foreground="black")

# ========== Interface principale ==========
root = tk.Tk()
root.title("📋 Application de Réservation")
root.state('zoomed')  # Ouvre la fenêtre maximisée (Windows)
frame_principal = tk.Frame(root, bg="white")
frame_form = tk.Frame(frame_principal, bg="white")
# Taille de la fenêtre (par exemple 1100x800)
window_width = 1100
window_height = 720

# Récupérer la taille de l'écran
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Calculer la position pour centrer la fenêtre
x = int((screen_width / 2) - (window_width / 2))
y = int((screen_height / 2) - (window_height / 2))

# Appliquer la géométrie centrée
root.geometry(f"{window_width}x{window_height}+{x}+{y}")
root.config(bg="white")

# Police principale pour toute l'app
FONT_MAIN = ("Segoe UI", 11)
FONT_TITLE = ("Segoe UI", 14, "bold")
FONT_BTN = ("Segoe UI", 11, "bold")

root.option_add("*Font", FONT_MAIN)
root.option_add("*Entry.Font", FONT_MAIN)
root.option_add("*Label.Font", FONT_MAIN)
root.option_add("*Button.Font", FONT_BTN)

# ========== Zone de formulaire ==========

frame_form = tk.Frame(frame_principal, bg="white")
frame_form.pack(pady=10)

# Créer deux frames pour la disposition gauche/droite
frame_gauche = tk.Frame(frame_form, bg="white")
frame_gauche.pack(side="left", padx=20)

frame_droite = tk.Frame(frame_form, bg="white")
frame_droite.pack(side="left", padx=20)

# Champs à gauche
entry_nom = champ("Nom", frame_gauche)

tk.Label(frame_gauche, text="Terrain demandé", bg="white").pack(anchor="w", pady=(0,2))
terrains = [
    "T.Chabab 1", "T.Chabab 2", "T.Chabab 3", "T.Chabab 4", "T.Chabab 5", "T.Chabab 6", "T.Chabab 7", "T.Chabab 8",
    "Salle Chabab 1", "Salle Chabab 2", "Salle Chabab 3", "Salle Moujahid",
    "T.Jawadi 1", "T.Jawadi 2", "Salle Fatima Ouam"
]
entry_terrain = ttk.Combobox(
    frame_gauche,
    values=terrains,
    state="readonly",
    width=25
)
entry_terrain.pack(pady=(0,8))

tk.Label(frame_gauche, text="Heure début", bg="white").pack(anchor="w", pady=(0,2))
heures_debut = [f"{h:02d}:00" for h in range(8, 24)]
entry_heure_debut = ttk.Combobox(
    frame_gauche,
    values=heures_debut,
    state="readonly",
    width=25
)
entry_heure_debut.pack(pady=(0,8))
entry_heure_debut.bind("<KeyRelease>", calculer_duree)
entry_heure_debut.bind("<<ComboboxSelected>>", calculer_duree)
entry_heure_debut.bind("<<ComboboxSelected>>", colorer_heure_debut)
entry_heure_debut.bind("<KeyRelease>", colorer_heure_debut)


tk.Label(frame_gauche, text="Durée (h)", bg="white").pack(anchor="w", pady=(0,2))
entry_duree = ttk.Entry(
    frame_gauche,
    width=25,
    state="readonly"
)
entry_duree.pack(pady=(0,8))

tk.Label(frame_gauche, text="Montant", bg="white").pack(anchor="w", pady=(0,2))
entry_montant = ttk.Combobox(
    frame_gauche,
    values=["60 DH", "100 DH", "150 DH"],
    state="readonly",
    width=25
)
entry_montant.pack(pady=(0,8))

# Champs à droite
tk.Label(frame_droite, text="Type de demandeur", bg="white").pack(anchor="w", pady=(0,2))
entry_type_demandeur = ttk.Combobox(
    frame_droite,
    values=["Citoyen", "Association", "École", "Autre"],
    state="readonly",
    width=25
)
entry_type_demandeur.pack(pady=(0,8))

tk.Label(frame_droite, text="Date", bg="white").pack(anchor="w", pady=(0,2))
entry_date = DateEntry(
    frame_droite,
    width=25,
    background="#f6f6f6",
    foreground="black",
    borderwidth=1,
    date_pattern="dd/MM/yyyy"
)
entry_date.pack(pady=(0,8))
entry_date.configure(state="readonly")  # Empêche la saisie manuelle

tk.Label(frame_droite, text="Heure fin", bg="white").pack(anchor="w", pady=(0,2))
heures_fin = heures_debut  # même valeurs que début
entry_heure_fin = ttk.Combobox(
    frame_droite,
    values=heures_fin,
    state="readonly",
    width=25
)
entry_heure_fin.pack(pady=(0,8))
entry_heure_fin.bind("<KeyRelease>", calculer_duree)
entry_heure_fin.bind("<<ComboboxSelected>>", calculer_duree)

entry_telephone = champ("Téléphone", frame_droite)
entry_telephone.insert(0, "+212")

def validate_telephone(new_value):
    # Autorise uniquement +212 suivi de 9 chiffres
    if not new_value.startswith("+212"):
        return False
    digits = new_value[4:]
    return digits.isdigit() and len(digits) <= 9

vcmd = (root.register(validate_telephone), "%P")
entry_telephone.config(validate="key", validatecommand=vcmd)

tk.Label(frame_droite, text="État de paiement", bg="white").pack(anchor="w", pady=(0,2))
entry_etat_paiement = ttk.Combobox(
    frame_droite,
    values=["Payé", "Non payé"],
    state="readonly",
    width=25
)
entry_etat_paiement.pack(pady=(0,8))

# ========== Zone de boutons (Ajouter, Modifier, Supprimer) ==========
frame_boutons = tk.Frame(frame_principal, bg="white")
frame_boutons.pack(pady=16)

style_btn = {
    "width": 16,
    "height": 2,
    "font": FONT_BTN,
    "bd": 0,
    "relief": "ridge",
    "activebackground": "#e0e0e0",
    "cursor": "hand2",
    "highlightthickness": 1,
    "highlightbackground": "#dddddd"
}


btn_supprimer = tk.Button(
    frame_boutons, text="Supprimer", bg="#dc3545", fg="white", command=supprimer, **style_btn
)
btn_supprimer.pack(side="left", padx=10)

btn_ajouter = tk.Button(
    frame_boutons, text="➕ Ajouter", bg="#28a745", fg="white", command=enregistrer, **style_btn
)
btn_ajouter.pack(side="left", padx=10)

def apercu_recu():
    selected = tableau.selection()
    if not selected:
        messagebox.showwarning("Aucune sélection", "Sélectionnez une réservation à prévisualiser.")
        return

    valeurs = tableau.item(selected[0])["values"]

    # Crée une nouvelle fenêtre d'aperçu
    win = tk.Toplevel(root)
    win.title("Aperçu du reçu")
    win.geometry("400x500")
    win.config(bg="white")

    # Affiche les infos sous forme de reçu
    titre = tk.Label(win, text="REÇU DE RÉSERVATION", font=("Segoe UI", 15, "bold"), bg="white")
    titre.pack(pady=10)

    frame = tk.Frame(win, bg="white")
    frame.pack(pady=10, padx=10, fill="both", expand=True)

    champs = [
        ("Numéro de réservation", valeurs[0]),
        ("Nom du Réservataire", valeurs[1]),
        ("Type de demandeur", valeurs[2]),
        ("Terrain demandé", valeurs[3]),
        ("Date de réservation", valeurs[4]),
        ("Heure début", valeurs[5]),
        ("Heure fin", valeurs[6]),
        ("Durée", valeurs[7]),
        ("Téléphone", valeurs[8]),
        ("Montant", valeurs[9]),
        ("État de paiement", valeurs[10]),
    ]

    for label, value in champs:
        row = tk.Frame(frame, bg="white")
        row.pack(fill="x", pady=2)
        tk.Label(row, text=label + " :", font=("Segoe UI", 10, "bold"), width=18, anchor="w", bg="white").pack(side="left")
        tk.Label(row, text=value, font=("Segoe UI", 10), anchor="w", bg="white").pack(side="left")

    tk.Label(win, text="Merci pour votre réservation.", font=("Segoe UI", 10, "italic"), bg="white").pack(pady=15)

btn_apercu = tk.Button(
    frame_boutons, text="Aperçu", bg="#17a2b8", fg="white", command=apercu_recu, **style_btn
)
btn_apercu.pack(side="left", padx=10)

btn_imprimer = tk.Button(
    frame_boutons, text="Imprimer", bg="#0078D7", fg="white", command=imprimer_direct, **style_btn
)
btn_imprimer.pack(side="left", padx=10)



def marquer_comme_paye():
    selected = tableau.selection()
    if not selected:
        messagebox.showwarning("Aucune sélection", "Sélectionnez une réservation.")
        return
    row_id = selected[0]
    valeurs = list(tableau.item(row_id)["values"])
    valeurs[10] = "Payé"
    tableau.item(row_id, values=valeurs)
    update_csv_row(row_id, valeurs)
    afficher_total_montant()


# ========== Recherche ==========
tk.Label(frame_principal, text="🔍 Recherche par nom :", bg="white", font=FONT_MAIN).pack()
entry_search = tk.Entry(frame_principal, width=30, bg="#f6f6f6", relief="flat", highlightthickness=1, highlightbackground="#cccccc")
entry_search.pack(pady=7, ipady=4)
entry_search.bind("<KeyRelease>", lambda event: rechercher())

# ========== Tableau + Scrollbars ==========

frame_tableau = tk.Frame(frame_principal, bg="white")
frame_tableau.pack(fill="both", expand=True, pady=10)

scroll_y = tk.Scrollbar(frame_tableau, orient="vertical")
scroll_x = tk.Scrollbar(frame_tableau, orient="horizontal")
scroll_y.pack(side="right", fill="y")
scroll_x.pack(side="bottom", fill="x")

colonnes = (
    "N°", "Nom", "Type de demandeur", "Terrain demandé", "Date",
    "Heure début", "Heure fin", "Durée", "Téléphone", "Montant", "État de paiement"
)
largeurs = [70, 110, 110, 110, 80, 70, 70, 70, 100, 70, 100]

tableau = ttk.Treeview(
    frame_tableau,
    columns=colonnes,
    show="headings",
    yscrollcommand=scroll_y.set,
    xscrollcommand=scroll_x.set
)

for col, w in zip(colonnes, largeurs):
    tableau.heading(col, text=col)
    tableau.column(col, width=w, anchor="center")

tableau.pack(side="left", fill="both", expand=True, padx=40, pady=5)
scroll_y.config(command=tableau.yview)
scroll_x.config(command=tableau.xview)

selected_item = None

# ========== Style pro pour le tableau ==========
style = ttk.Style()
style.theme_use("default")

# En-tête
style.configure("Treeview.Heading",
    background="#145A32",  # Vert (Bootstrap green)
    foreground="white",
    font=("Segoe UI Semibold", 11),
    relief="flat"
)
# Désactive le hover blanc sur l'en-tête
style.map("Treeview.Heading",
    background=[("active", "#0078D7")],
    foreground=[("active", "white")]
)

# Lignes
style.configure("Treeview",
    font=("Segoe UI", 11),
    rowheight=28,
    background="#f8fafc",
    fieldbackground="#f8fafc",
    borderwidth=0,
    foreground="#222"   # <-- Ajoute cette ligne pour forcer le texte noir par défaut
)

# Lignes alternées
style.map("Treeview",
    background=[("selected", "#0078D7")],
    foreground=[("selected", "#fff")]  # Texte blanc sur fond bleu sélectionné
)

style.layout("Treeview", [
    ('Treeview.treearea', {'sticky': 'nswe'})
])

# Configure les tags UNE SEULE FOIS
tableau.tag_configure("evenrow", background="#f8fafc", foreground="#222")
tableau.tag_configure("oddrow", background="#e9f1fb", foreground="#222")

def tag_rows():
    for i, item in enumerate(tableau.get_children()):
        if i % 2 == 0:
            tableau.item(item, tags=("evenrow",))
        else:
            tableau.item(item, tags=("oddrow",))

# ========== Lancement ==========
charger_tableau()
tag_rows()
entry_date.bind("<<DateEntrySelected>>", update_heures_disponibles)
update_heures_disponibles()

# 1. Label en haut à droite
label_total = tk.Label(frame_principal, text="💰 Total : 0.00 DH", font=("Segoe UI", 13, "bold"), bg="white", fg="#28a745")
label_total.place(relx=0.98, rely=0.01, anchor="ne")  # En haut à droite

# 2. Fonction de calcul du total
def afficher_total_montant():
    total = 0
    for item in tableau.get_children():
        valeurs = tableau.item(item)["values"]
        try:
            montant_str = str(valeurs[9]).replace("DH", "").replace("dh", "").strip()
            etat = str(valeurs[10]).strip().lower()
            if etat == "payé":
                montant = float(montant_str)
                total += montant
        except:
            pass
    label_total.config(text=f"💰 Total : {total:.2f} DH")

afficher_total_montant()  # <-- ici

show_total = [False]  # Utilise une liste pour mutabilité

def toggle_total():
    show_total[0] = not show_total[0]
    if show_total[0]:
        label_total.place(relx=0.93, rely=0.01, anchor="ne")  # Place le total à gauche de l'œil
        btn_eye.config(text="🙈")
    else:
        label_total.place_forget()
        btn_eye.config(text="👁️")

btn_eye = tk.Button(
    frame_principal, text="👁️", command=toggle_total,
    bg="white", bd=0, font=("Segoe UI", 15), activebackground="white", cursor="hand2"
)
btn_eye.place(relx=0.98, rely=0.01, anchor="ne")  # Place l'œil à droite

label_total.place_forget()  # Cache le total au démarrage

def edit_cell(event):
    region = tableau.identify("region", event.x, event.y)
    if region != "cell":
        return
    row_id = tableau.identify_row(event.y)
    col_id = tableau.identify_column(event.x)
    col_index = int(col_id.replace("#", "")) - 1

    # Autorise l'édition de toutes les colonnes
    x, y, width, height = tableau.bbox(row_id, col_id)
    value = tableau.item(row_id)["values"][col_index]

    entry_edit = tk.Entry(tableau, width=18, font=FONT_MAIN)
    entry_edit.place(x=x, y=y, width=width, height=height)
    entry_edit.insert(0, value)
    entry_edit.focus_set()

    def save_edit(event=None):
        new_value = entry_edit.get()
        values = list(tableau.item(row_id)["values"])
        values[col_index] = new_value
        tableau.item(row_id, values=values)
        entry_edit.destroy()
        update_csv_row(row_id, values)
        afficher_total_montant()  # Met à jour le total

    entry_edit.bind("<Return>", save_edit)
    entry_edit.bind("<FocusOut>", lambda e: entry_edit.destroy())

tableau.bind("<Double-1>", edit_cell)

def update_csv_row(row_id, new_values):
    numero = new_values[0]
    lignes = []
    with open("reservations.csv", mode='r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        entete = next(reader)
        lignes.append(entete)
        for row in reader:
            if str(row[0]) == str(numero):
                lignes.append(list(new_values))
            else:
                lignes.append(row)
    with open("reservations.csv", mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(lignes)


# ========== Connexion ==========

def show_login_inplace(root, frame_principal):
    # Fond gris clair pour la fenêtre principale
    root.config(bg="#f3f6fa")
    # Frame centré, plus large
    frame_login = tk.Frame(root, bg="white", bd=0, highlightthickness=0)
    frame_login.place(relx=0.5, rely=0.5, anchor="center", width=400, height=370)

    # Icône (plus haut)
    logo = tk.Label(frame_login, text="🔒", font=("Segoe UI Emoji", 44), bg="white")
    logo.place(relx=0.5, rely=0.13, anchor="center")

    # Titre
    tk.Label(frame_login, text="Connexion", bg="white", fg="#0078D7", font=("Segoe UI", 18, "bold")).place(relx=0.5, rely=0.28, anchor="center")

    # Champ utilisateur avec padding (fond blanc, border arrondi, padding interne)
    frame_user = tk.Frame(frame_login, bg="white", highlightbackground="#d1d9e6", highlightthickness=1, bd=0)
    frame_user.place(relx=0.5, rely=0.40, anchor="center", height=36, width=270)
    entry_user = tk.Entry(frame_user, width=28, font=("Segoe UI", 13), bd=0, bg="white",
                          relief="flat", highlightthickness=0, insertbackground="#222")
    entry_user.pack(fill="both", expand=True, padx=12)
    entry_user.config(fg="#222")

    # Champ mot de passe avec padding (fond blanc, border arrondi, padding interne)
    frame_pass = tk.Frame(frame_login, bg="white", highlightbackground="#d1d9e6", highlightthickness=1, bd=0)
    frame_pass.place(relx=0.5, rely=0.53, anchor="center", height=36, width=270)
    entry_pass = tk.Entry(frame_pass, width=28, font=("Segoe UI", 13), bd=0, bg="white",
                          relief="flat", highlightthickness=0, show="*", insertbackground="#222")
    entry_pass.pack(fill="both", expand=True, padx=12)
    entry_pass.config(fg="#222")

    # Message d'erreur
    label_error = tk.Label(frame_login, text="", fg="#dc3545", bg="white", font=("Segoe UI", 10, "bold"))
    label_error.place(relx=0.5, rely=0.62, anchor="center")

    # Bouton connexion stylé
    def try_login():
        user = entry_user.get()
        pwd = entry_pass.get()
        if user == "admin" and pwd == "admin123":
            frame_login.destroy()
            root.config(bg="white")
            frame_principal.pack(fill="both", expand=True)
        else:
            label_error.config(text="Identifiants incorrects !")

    btn = tk.Button(
        frame_login, text="Se connecter", bg="#0078D7", fg="white",
        font=("Segoe UI", 13, "bold"), width=20, height=1, bd=0,
        activebackground="#005fa3", activeforeground="white",
        cursor="hand2", command=try_login
    )
    btn.place(relx=0.5, rely=0.74, anchor="center", height=38)

    # Copyright ou info
    tk.Label(frame_login, text="© 2025 Arrondissement Ben M'sick", bg="white", fg="#aaa", font=("Segoe UI", 9)).place(relx=0.5, rely=0.90, anchor="center")

    entry_user.focus_set()

# ========== Lancement de l'application ==========

# Affiche la fenêtre de connexion en premier
show_login_inplace(root, frame_principal)
root.mainloop()

