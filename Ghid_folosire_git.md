# 🧭 Ghid Git pentru proiect – Workflow cu branch-uri

Acest fișier explică, pas cu pas, cum lucrăm cu Git în acest proiect:
- cum îți setezi mediul
- cum creezi un branch nou
- cum faci commit-uri
- cum faci push
- cum faci merge în `main`

---

## 1. Configurare inițială Git (o singură dată pe calculator)

Setează numele și emailul (apar în istoricul de commit):

```bash
git config --global user.name "Numele Tau"
git config --global user.email "emailul@tau.com"
Verifici:

git config --global --list
2. Clonarea repository-ului

Dacă nu ai încă proiectul local:

git clone <URL_REPO_GIT>
cd <nume_folder_proiect>


Exemplu:

git clone https://github.com/user/Predictia-aglomerarii-sali.git
cd Predictia-aglomerarii-sali

3. Verificarea statusului proiectului

Oricând vrei să vezi ce s-a schimbat:

git status


„nothing to commit, working tree clean” → totul e salvat

fișiere roșii → modificate, dar NEadăugate

fișiere verzi → adăugate, dar NEcomitate

4. Actualizarea branch-ului main înainte de lucru

Înainte să începi să lucrezi la ceva nou:

git checkout main        # sau: git switch main
git pull                 # aduce ultimele modificări de pe remote


Astfel ești sigur că lucrezi pe ultima versiune a proiectului.

5. Crearea unui branch nou

Folosim branch-uri pentru fiecare feature / task, ca să nu stricăm main.

Variantă recomandată (1 singură comandă):
git checkout -b nume-branch


Exemple de denumiri recomandate:

feature-gym-list-api

bugfix-predictor-time

Antonel (pentru lucru personal, cum ai acum)

Această comandă:

creează branch-ul

te mută automat pe el

Verifici:

git branch


Cu * este branch-ul curent.

6. Lucru pe branch-ul tău

După ce ai creat branch-ul și ai modificat fișierele:

Vezi ce s-a schimbat:
git status

Adaugi fișierele modificate:

Toate fișierele:

git add .


sau doar anumite fișiere:

git add frontend/src/components/GymList.jsx
git add backend/main.py

Creezi un commit:
git commit -m "Descriere scurtă și clară a modificărilor"


Exemple de mesaje bune:

"Adaugare GymsList si endpoint /sali"

"Conectare FastAPI la baza de date MySQL"

"Refactorizare PredictorCard si stilizare UI"

7. Push al branch-ului pe remote (GitHub)

Prima dată pentru un branch nou:

git push -u origin nume-branch


După ce ai setat -u, mai departe poți folosi doar:

git push


Acum colegii tăi pot vedea branch-ul tău în remote.

8. Integrarea branch-ului tău în main (merge)

Când ai terminat de lucrat pe branch-ul tău (Antonel, feature-xyz etc.) și totul e testat:

1) Asigură-te că TOTUL este comitat
git status


Trebuie să fie:

nothing to commit, working tree clean
2) Mergi pe main:
git checkout main

3) Aduce ultimele modificări de pe remote:
git pull

4) Faci merge din branch-ul tău în main:
git merge nume-branch


Exemplu:

git merge Antonel


Dacă nu apar conflicte, commit-ul de merge se face automat.

5) Trimiți main actualizat pe remote:
git push


Acum main conține tot ce ai făcut în branch.

9. Ștergerea unui branch după merge (opțional, dar recomandat)

După ce ai integrat branch-ul în main:

Ștergere locală:
git branch -d nume-branch

Ștergere din remote:
git push origin --delete nume-branch


De obicei, la branch-uri de tip feature-..., e recomandat să le ștergi după ce sunt integrate, pentru a nu aglomera repo-ul.



********************
10. Workflow recomandat pentru fiecare task

Rezumat:

# 1. Actualizează main
git checkout main
git pull

# 2. Creează branch nou din main
git checkout -b feature-nume-task

# 3. Lucrezi, modifici fișiere

# 4. Salvezi schimbările
git add .
git commit -m "Descriere task"

# 5. Push pentru backup / colaborare
git push -u origin feature-nume-task

# 6. Când ai terminat: merge în main
git checkout main
git pull
git merge feature-nume-task
git push

# 7. (Opțional) curățenie
git branch -d feature-nume-task
git push origin --delete feature-nume-task