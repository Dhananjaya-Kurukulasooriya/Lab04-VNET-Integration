import azure.functions as func
import logging
import json




app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Getting weather-based menu through VNet')
    
    try:
        # Get parameters from request
        city = req.params.get('city', 'NewYork')
        customer_type = req.params.get('customerType', 'regular')
        
        # Call weather API to get current temperature
        weather_data = get_weather_data(city)
        
        # Calculate weather-based menu and discounts
        menu = calculate_weather_menu(weather_data, customer_type)
        
        response = {
            'message': 'Weather-based menu generated via VNet',
            'city': city,
            'weather': weather_data,
            'customerType': customer_type,
            'recommendedDrinks': menu['drinks'],
            'pricing': menu['pricing'],
            'weatherDiscount': menu['weather_discount'],
            'totalDiscount': menu['total_discount'],
            'reason': menu['reason']
        }
        
        return func.HttpResponse(
            json.dumps(response, indent=2),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f'Error: {str(e)}')
        
        # Fallback response if weather API fails
        fallback = {
            'message': 'Using fallback menu (weather API unavailable)',
            'city': city,
            'recommendedDrinks': ['Classic Coffee', 'Hot Chocolate'],
            'pricing': {'regular': 4.99, 'large': 6.99},
            'weatherDiscount': 0,
            'totalDiscount': 0,
            'reason': 'Weather service unavailable'
        }
        
        return func.HttpResponse(
            json.dumps(fallback, indent=2),
            status_code=200,
            mimetype="application/json"
        )

def get_weather_data(city):
    """Get weather data for the city"""
    try:
        # Using OpenWeatherMap API (free tier)
        # Note: In production, you'd use your own API key
        api_key = "demo"  # This is a demo key, limited functionality
        
        # For demo purposes, simulate weather data based on city
        weather_simulation = simulate_weather_by_city(city)
        
        return weather_simulation
        
    except Exception as e:
        logging.error(f'Weather API error: {str(e)}')
        # Return default weather if API fails
        return {'temperature': 20, 'condition': 'clear', 'city': city}

def simulate_weather_by_city(city):
    """Simulate weather data for demo purposes"""
    # In real scenario, this would be actual API call
    city_weather = {
        'miami': {'temperature': 32, 'condition': 'hot', 'city': 'Miami'},
        'newyork': {'temperature': 18, 'condition': 'cool', 'city': 'New York'},
        'seattle': {'temperature': 12, 'condition': 'cold', 'city': 'Seattle'},
        'phoenix': {'temperature': 38, 'condition': 'very hot', 'city': 'Phoenix'},
        'chicago': {'temperature': 8, 'condition': 'very cold', 'city': 'Chicago'}
    }
    
    return city_weather.get(city.lower(), {'temperature': 22, 'condition': 'mild', 'city': city})

def calculate_weather_menu(weather_data, customer_type):
    """Calculate menu based on weather and customer type"""
    temperature = weather_data['temperature']
    city = weather_data['city']
    
    base_price = 4.99
    weather_discount = 0
    customer_discount = 0
    
    # Weather-based drink recommendations and discounts
    if temperature >= 30:  # Very hot
        drinks = ['Iced Coffee', 'Cold Brew', 'Frappuccino', 'Iced Tea']
        weather_discount = 20  # 20% off cold drinks on very hot days
        reason = f"🌡️ Very hot day in {city} ({temperature}°C) - 20% off all iced drinks!"
        
    elif temperature >= 25:  # Hot
        drinks = ['Iced Coffee', 'Cold Brew', 'Iced Latte']
        weather_discount = 15  # 15% off cold drinks on hot days
        reason = f"☀️ Hot day in {city} ({temperature}°C) - 15% off cold drinks!"
        
    elif temperature <= 5:  # Very cold
        drinks = ['Hot Chocolate', 'Espresso', 'Cappuccino', 'Hot Tea']
        weather_discount = 20  # 20% off hot drinks on very cold days
        reason = f"🧊 Very cold day in {city} ({temperature}°C) - 20% off all hot drinks!"
        
    elif temperature <= 15:  # Cold
        drinks = ['Hot Coffee', 'Latte', 'Cappuccino', 'Hot Chocolate']
        weather_discount = 15  # 15% off hot drinks on cold days
        reason = f"❄️ Cold day in {city} ({temperature}°C) - 15% off hot drinks!"
        
    else:  # Mild weather
        drinks = ['Coffee', 'Latte', 'Cappuccino', 'Tea']
        weather_discount = 5   # Small discount for regular weather
        reason = f"🌤️ Nice weather in {city} ({temperature}°C) - 5% off all drinks!"
    
    # Customer type additional discounts
    if customer_type.lower() == 'student':
        customer_discount = 10
    elif customer_type.lower() == 'premium':
        customer_discount = 5
    
    # Calculate final pricing
    total_discount = weather_discount + customer_discount
    final_price = base_price * (1 - total_discount / 100)
    
    return {
        'drinks': drinks,
        'pricing': {
            'base_price': base_price,
            'final_price': round(final_price, 2),
            'size': 'Regular'
        },
        'weather_discount': weather_discount,
        'customer_discount': customer_discount,
        'total_discount': total_discount,
        'reason': reason
    }

