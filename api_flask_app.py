from flask import Flask, make_response, request, render_template, url_for
import os
from analyser import main_script
from markdown import markdown

app = Flask(__name__)
app.config['SECRET_KEY'] = '6Ed2)2Ou,0T?DB+'


# landing page for application
@app.route('/')
def welcome():
    return render_template("ui.html")


@app.route('/scan', methods=['POST'])
def scan_file():
    try:
        # get file from UI and save it in local storage
        f = request.files['file']
        prompt = request.values['comment']
        f.save(os.path.join("payloads", f.filename))
        path = str(os.path.join("payloads", f.filename))

        # FILE SIZE VALIDATION
        size = os.path.getsize(path)
        if size > 20000000:
            print("File is greater than 20MB")
            os.remove(path)
            return make_response(
                'File Size Exceeds than 20MB.',
                200
            )

        response = main_script(prompt, path)
        # print(response)

        return render_template('response.html', response=markdown(response))

    except Exception as e:
        print(e)
        return make_response(
            str("Server was unable to understand the request."),
            200
        )

if __name__ == "__main__":
    app.run(host ='0.0.0.0', port=5000, debug=True)
