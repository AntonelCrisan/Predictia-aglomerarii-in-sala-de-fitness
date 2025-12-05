import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt
import joblib

# 1. Încărcarea datelor
dataAfterCleaning = pd.read_csv('dataAfterCleaning.csv', header=None) 
dataSetForLearning = pd.read_csv('dataSetForLearning.csv', header=None)
dataPeople = pd.read_csv('dataPeople.csv', header=None)
dataPeopleNew = pd.read_csv('dataPeopleNew.csv', header=None)
dataSetForLearningNew = pd.read_csv('dataSetForLearningNew.csv', header=None)

# 2. Separarea caracteristicilor & variabilei țintă
X = dataSetForLearning
y = dataPeople.values.ravel()   # transformăm într-un vector 1D

# 3. Împărțirea în train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 4. Inițializare și antrenare RandomForest
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# 5. Scor pe setul de testare
rf_score = rf_model.score(X_test, y_test)
print("Scorul Random Forest Regressor:", rf_score)

# 6. Predicții pe test
predictions_rf = rf_model.predict(X_test)

# 7. Calcul MAE și MSE
mae_rf = mean_absolute_error(y_test, predictions_rf)
print("Eroarea absolută medie (MAE) pentru Random Forest:", mae_rf)

mse_rf = mean_squared_error(y_test, predictions_rf)
print("Eroarea medie pătratică (MSE) pentru Random Forest:", mse_rf)

# 8. Plot
plt.figure(figsize=(10, 6))
plt.scatter(y_test, predictions_rf, color='green', label='Valori prezise (Random Forest)')
plt.plot(y_test, y_test, color='red', linestyle='--', label='Linie de regresie')
plt.title('Predicțiile Random Forest vs. Valori reale')
plt.xlabel('Valori reale')
plt.ylabel('Valori prezise')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# 9. Salvare model antrenat
joblib.dump(rf_model, "rf_model.pkl")
print("Modelul a fost salvat în fișierul rf_model.pkl")
