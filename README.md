
*Rain Cloud Predicting with Cloud Computing - A Personal Weather/Pollution Alert System Built with Python, AWS Lambda, and Weather APIs*


What You'll Need
Requirements:
A Telegram bot token & chat ID (Telegram is easy to integrate, Watsapp needs additional overheads, which I can cover in future articles)
An AWS account (for Lambda + CloudWatch Scheduler)
Weather API keys (we'll use two: OpenWeatherMap , WeatherAPI, Iqair API)
Basic Python and AWS CLI knowledge

How It Works
User inputs location (latitude and longitude), through a config file. 
Lambda function runs every 5 minutes, via cron triggered via Cloudwatch 
It queries two weather APIs for rain predictions and gathers weather details. It also gathers pollution information for the location.
If both predict rain with high confidence, a Telegram message is sent
