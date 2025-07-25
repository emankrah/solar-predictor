<h2> Solar Energy Predictor Api</h2>

    This model takes in features irradiance ,temperautre , the hour and humidity and predicts the energy that the solar panel would be able to produce in that particular hour.

<h2>Key Challenges faceed</h2>
    This model is trained on fictious data , these arent real solar panel output , we used a formula that would calulate the power of the solar panel in this formula we used the wattage 20W. That is the rating of our solar panel at perfect conditions.

    Also,we used 10 years worth of weather data to train this model , however the model couldnt quite the relationhip between time and the output quite well so we hard coded it. 

    The hour feature is further broken down into hr_sin and hr_cos . The model picks this up better than the feature , just hr . So i have included it , The calulation for the hr_sin and hr_cos would be done by the api and not the user.



<b>That is abput it for now</b>