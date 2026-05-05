## 🚦 AI Traffic Flow Optimizer

## 📌 Overview
This project aims to optimize traffic signal timing using algorithmic and data-driven techniques to reduce congestion and improve traffic flow efficiency. It provides an interactive dashboard to analyze traffic conditions and make intelligent decisions.

## ⚙️ Features
- 🚦 Dynamic traffic signal timing  
- 📊 Traffic congestion analysis  
- 🧠 Machine learning-based prediction  
- 📈 Data visualization for traffic patterns  
- 🌐 Interactive web dashboard using Flask  

## 🛠️ Tech Stack
- Python  
- Flask  
- Machine Learning (K-Means, Linear Regression, Decision Tree)  
- Pandas, NumPy, Matplotlib  

## 🚀 How to Run

### 1. Clone the repository
git clone https://github.com/snehasrinivas585-lab/ai-traffic-project


### 2. Navigate to the project folder

cd ai-traffic-project


### 3. Run the application

py notebooks/app.py


### 4. Open in browser

http://127.0.0.1:5000/


## 📊 Output

### 🏠 Home Page
The home page acts as the central dashboard of the application. It displays:
- Traffic prediction input section (average speed input)  
- Visualizations of machine learning models such as K-Means clustering and Linear Regression  
- Graphs to understand traffic patterns and model performance  
![Home](notebooks/static/images/home.png)

### 📊 Prediction Output
In this section, the user enters the average vehicle speed, and the system predicts the traffic condition:
- 🚨 High Traffic (low speed)  
- ⚠ Medium Traffic  
- ✅ Low Traffic (high speed)  
![Prediction](notebooks/static/images/prediction.png)

This helps in identifying congestion levels based on input data.

### 🚦 Signal Optimization
This section allows users to input traffic density from four directions (North, South, East, West).

The system then:
- Calculates total traffic load  
- Identifies the priority lane (highest traffic)  
- Assigns optimal green signal time  
- Displays overall traffic status (Low / Moderate / Heavy)  
![Signal](notebooks/static/images/signal.png)

This helps in dynamically managing traffic signals and reducing congestion.

## 📈 Future Improvements
- Integration with real-time traffic data  
- Advanced machine learning models  
- Deployment as a live web application  

## 👩‍💻 Author
Sneha Srinivas  
GitHub: https://github.com/snehasrinivas585-lab