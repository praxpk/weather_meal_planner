Run the python file weather_api.py
if using windows follow these instructions:
<br>
open command window (cmd)
<br>
change the directory to the weatherAPI folder.
<br>
type the following
<br>
(if flask is not installed)
>pip install flask

>set FLASK_APP=weather_api.py

>set FLASK_ENV=development

>flask run
<br>

if mac os or linux:
>export FLASK_APP=weather_api.py

>flask run

After running the above commands, open a browser and type:
http://127.0.0.1:5000/ 

Type the zipcode (US ONLY) and wait for the results.