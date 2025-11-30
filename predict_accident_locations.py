"""
Accident Location Prediction using Machine Learning
Predicts 30 most likely accident locations based on accident type, weather, vehicle type, and population.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

# Load data
print("Loading data...")
df = pd.read_csv('data/accidents/economic_impact_population.csv')

# Remove rows with missing LAT/LON
df = df.dropna(subset=['LATITUDE', 'LONGITUDE'])

# Remove rows with missing features
df = df.dropna(subset=['ACCIDENT_TYPE_(CATEGORY)', 'WEATHER', 'VEHICLE_1:_BODY_TYPE', 'POPULATION', 'IMPACT'])

print(f"Total records: {len(df)}")

# Encode categorical variables
print("\nEncoding categorical features...")
le_accident = LabelEncoder()
le_weather = LabelEncoder()
le_vehicle = LabelEncoder()

df['accident_encoded'] = le_accident.fit_transform(df['ACCIDENT_TYPE_(CATEGORY)'])
df['weather_encoded'] = le_weather.fit_transform(df['WEATHER'])
df['vehicle_encoded'] = le_vehicle.fit_transform(df['VEHICLE_1:_BODY_TYPE'])

# Prepare features and targets
X = df[['accident_encoded', 'weather_encoded', 'vehicle_encoded', 'POPULATION']]
y_lat = df['LATITUDE']
y_lon = df['LONGITUDE']
y_impact = df['IMPACT']

# Split data
X_train, X_test, y_lat_train, y_lat_test, y_lon_train, y_lon_test, y_imp_train, y_imp_test = train_test_split(
    X, y_lat, y_lon, y_impact, test_size=0.2, random_state=42
)

# Train models
print("\nTraining Random Forest models...")
print("Training Latitude predictor...")
model_lat = RandomForestRegressor(n_estimators=100, max_depth=20, random_state=42, n_jobs=-1)
model_lat.fit(X_train, y_lat_train)

print("Training Longitude predictor...")
model_lon = RandomForestRegressor(n_estimators=100, max_depth=20, random_state=42, n_jobs=-1)
model_lon.fit(X_train, y_lon_train)

print("Training Impact predictor...")
model_impact = RandomForestRegressor(n_estimators=200, max_depth=20, random_state=42, n_jobs=-1)
model_impact.fit(X_train, y_imp_train)

# Evaluate
lat_pred = model_lat.predict(X_test)
lon_pred = model_lon.predict(X_test)
impact_pred = model_impact.predict(X_test)

lat_mae = mean_absolute_error(y_lat_test, lat_pred)
lon_mae = mean_absolute_error(y_lon_test, lon_pred)
impact_mae = mean_absolute_error(y_imp_test, impact_pred)

print(f"\nModel Performance:")
print(f"Latitude MAE: {lat_mae:.6f} degrees (~{lat_mae * 111:.2f} km)")
print(f"Longitude MAE: {lon_mae:.6f} degrees (~{lon_mae * 111:.2f} km)")
print(f"Impact MAE: {impact_mae:.3f} (impact units)")

# Create mock scenarios
print("\nCreating mock scenarios...")

# Get unique values
accident_types = df['ACCIDENT_TYPE_(CATEGORY)'].unique()
weather_conditions = df['WEATHER'].unique()
vehicle_types = df['VEHICLE_1:_BODY_TYPE'].unique()

# Population range (reasonable values from the data)
pop_min = df['POPULATION'].quantile(0.25)
pop_max = df['POPULATION'].quantile(0.75)

# Generate 30 diverse scenarios
np.random.seed(42)
scenarios = []

for i in range(30):
    scenario = {
        'ACCIDENT_TYPE_(CATEGORY)': np.random.choice(accident_types),
        'WEATHER': np.random.choice(weather_conditions),
        'VEHICLE_1:_BODY_TYPE': np.random.choice(vehicle_types),
        'POPULATION': np.random.randint(int(pop_min), int(pop_max))
    }
    scenarios.append(scenario)

scenarios_df = pd.DataFrame(scenarios)

# Encode scenarios
scenarios_df['accident_encoded'] = le_accident.transform(scenarios_df['ACCIDENT_TYPE_(CATEGORY)'])
scenarios_df['weather_encoded'] = le_weather.transform(scenarios_df['WEATHER'])
scenarios_df['vehicle_encoded'] = le_vehicle.transform(scenarios_df['VEHICLE_1:_BODY_TYPE'])

# Prepare features for prediction
X_scenarios = scenarios_df[['accident_encoded', 'weather_encoded', 'vehicle_encoded', 'POPULATION']]

# Predict locations
print("\nPredicting accident locations...")
predicted_lat = model_lat.predict(X_scenarios)
predicted_lon = model_lon.predict(X_scenarios)
predicted_impact = model_impact.predict(X_scenarios)

# Create results dataframe
results = scenarios_df[['ACCIDENT_TYPE_(CATEGORY)', 'WEATHER', 'VEHICLE_1:_BODY_TYPE', 'POPULATION']].copy()
results['PREDICTED_LATITUDE'] = predicted_lat
results['PREDICTED_LONGITUDE'] = predicted_lon
results['PREDICTED_IMPACT'] = predicted_impact

# Save results
output_file = 'data/accidents/predicted_locations.csv'
results.to_csv(output_file, index=False)

print(f"\n✅ Prediction complete!")
print(f"📁 Results saved to: {output_file}")
print(f"\n📊 Sample predictions:")
print(results.head(10).to_string(index=False))

print(f"\n🎯 Total predictions: {len(results)}")
print(f"\n📍 Latitude range: {predicted_lat.min():.4f} to {predicted_lat.max():.4f}")
print(f"📍 Longitude range: {predicted_lon.min():.4f} to {predicted_lon.max():.4f}")
print(f"💥 Impact range: {predicted_impact.min():.2f} to {predicted_impact.max():.2f}")
