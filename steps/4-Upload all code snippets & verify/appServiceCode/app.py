# Simple Coffee Shop Flask App - Single File
# File: app.py

from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Your Azure Function URL (replace with your actual function URL after deployment)
FUNCTION_URL = os.environ.get('FUNCTION_URL', "https://getwether.azurewebsites.net/api/http_trigger")

@app.route('/')
def home():
    """Simple home page with form"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Coffee Shop</title>
        <style>
            body { font-family: Arial; max-width: 500px; margin: 50px auto; padding: 20px; }
            input, select { width: 100%; padding: 10px; margin: 10px 0; }
            button { background: brown; color: white; padding: 15px; width: 100%; border: none; }
            .info { background: #f0f0f0; padding: 15px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <h1>☕ Coffee Shop</h1>
        <p>Get coffee recommendations based on weather</p>
        
        <form action="/menu" method="POST">
            <label>Your City:</label>
            <select name="city" required>
                <option value="">Select city</option>
                <option value="Phoenix">Phoenix (Hot)</option>
                <option value="Miami">Miami (Warm)</option>
                <option value="NewYork">New York (Mild)</option>
                <option value="Seattle">Seattle (Cool)</option>
                <option value="Chicago">Chicago (Cold)</option>
            </select>
            
            <label>Customer Type:</label>
            <select name="customer_type" required>
                <option value="regular">Regular</option>
                <option value="student">Student (10% extra off)</option>
                <option value="premium">Premium (5% extra off)</option>
            </select>
            
            <button type="submit">Get Menu</button>
        </form>
        
        <div class="info">
            <b>How it works:</b><br>
            • Hot weather = iced drinks discount<br>
            • Cold weather = hot drinks discount<br>
            • Extreme weather = bigger discounts
        </div>
    </body>
    </html>
    """
    return html

@app.route('/menu', methods=['POST'])
def menu():
    """Get menu from Azure Function and show results"""
    try:
        city = request.form.get('city')
        customer_type = request.form.get('customer_type')
        
        # Call Azure Function through VNet
        params = {'city': city, 'customerType': customer_type}
        response = requests.get(FUNCTION_URL, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            return show_menu(data, city)
        else:
            return show_error(f"Function returned error: {response.status_code}")
            
    except Exception as e:
        return show_error(f"Error: {str(e)}")

def show_menu(data, city):
    """Show the menu results"""
    drinks_list = "<br>".join([f"• {drink}" for drink in data['recommendedDrinks']])
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Your Menu - Coffee Shop</title>
        <style>
            body {{ font-family: Arial; max-width: 600px; margin: 50px auto; padding: 20px; }}
            .box {{ background: #f9f9f9; padding: 15px; margin: 15px 0; border-left: 4px solid #333; }}
            .weather {{ background: #e8f5e8; border-left-color: green; }}
            .discount {{ background: #ffe8e8; border-left-color: red; }}
            .pricing {{ background: #e8e8ff; border-left-color: blue; }}
            .price {{ font-size: 1.5em; font-weight: bold; color: green; }}
            button {{ background: brown; color: white; padding: 10px 20px; border: none; }}
        </style>
    </head>
    <body>
        <h1>☕ Your Menu for {city}</h1>
        
        <div class="box weather">
            <h3>🌡️ Weather Info</h3>
            <p><b>Temperature:</b> {data['weather']['temperature']}°C</p>
            <p><b>Condition:</b> {data['weather']['condition']}</p>
        </div>
        
        <div class="box discount">
            <h3>🎉 Today's Offer</h3>
            <p>{data['reason']}</p>
            <p><b>Weather Discount:</b> {data['weatherDiscount']}%</p>
            <p><b>Total Discount:</b> {data['totalDiscount']}%</p>
        </div>
        
        <div class="box">
            <h3>🍵 Recommended Drinks</h3>
            {drinks_list}
        </div>
        
        <div class="box pricing">
            <h3>💰 Pricing</h3>
            <p>Regular Price: ${data['pricing']['base_price']}</p>
            <p class="price">Your Price: ${data['pricing']['final_price']}</p>
            <p>You Save: ${data['pricing']['base_price'] - data['pricing']['final_price']:.2f}</p>
        </div>
        
        <button onclick="window.location.href='/'">← Back to Home</button>
        
        <div class="box" style="margin-top: 30px; font-size: 12px; color: #666;">
            <b>Technical:</b> {data['message']}<br>
            <b>VNet:</b> Web app called Azure Function through private network
        </div>
    </body>
    </html>
    """
    return html

def show_error(error_msg):
    """Show error page"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Error - Coffee Shop</title>
        <style>
            body {{ font-family: Arial; max-width: 500px; margin: 50px auto; padding: 20px; text-align: center; }}
            .error {{ background: #ffe8e8; padding: 20px; margin: 20px 0; border: 1px solid red; }}
            button {{ background: brown; color: white; padding: 10px 20px; border: none; margin: 10px; }}
        </style>
    </head>
    <body>
        <h1>☕ Oops!</h1>
        
        <div class="error">
            {error_msg}
        </div>
        
        <p><b>What to check:</b></p>
        <ul style="text-align: left;">
            <li>Is your Azure Function running?</li>
            <li>Is VNet integration working?</li>
            <li>Is the Function URL correct?</li>
        </ul>
        
        <button onclick="window.location.href='/'">← Back to Home</button>
        <button onclick="location.reload()">Try Again</button>
    </body>
    </html>
    """
    return html

@app.route('/health')
def health():
    """Simple health check"""
    return {"status": "ok", "message": "Coffee shop is running!"}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)