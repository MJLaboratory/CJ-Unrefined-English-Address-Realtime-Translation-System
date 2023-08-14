# from flask import Flask, render_template

# app = Flask(__name__)

# @app.route("/")
# def index():
#     return render_template('./index.html')

from flask import Flask, request, jsonify
import Ifright4_v21.1 as IFR
app = Flask(__name__)

def process_address(address):
    #address = Ifright.get_translated_address(address)
    address = IFR.get_translated_address(address)
    return address

@app.route('/process_requests', methods=['POST'])
def process_requests():
    data = request.get_json()

    if not data or 'requestList' not in data:
        return jsonify({"HEADER": {"RESULT_CODE": "E", "RESULT_MSG": "Invalid data format"}}), 400

    request_list = data['requestList']

    processed_requests = []
    failed_requests = []

    for req in request_list:
        seq = req.get('seq')
        address = req.get('requestAddress')

        if seq and address:
            processed_address = process_address(address)
            processed_requests.append({
                "seq": seq,
                "resultAddress": processed_address
            })
        else:
            failed_requests.append({
                "seq": seq,
                "resultAddress": address
            })

    response_data = {
        "HEADER": {
            "RESULT_CODE": "S" if not failed_requests else "F",
            "RESULT_MSG": "Success" if not failed_requests else "Some requests failed"
        },
        "BODY": processed_requests
    }

    if failed_requests:
        for failed_req in failed_requests:
            error_msg = f"seq {failed_req['seq']} is failed to transfer"
            response_data["HEADER"]["RESULT_CODE"] = "F"
            response_data["HEADER"]["RESULT_MSG"] = error_msg

    return jsonify(response_data), 200

if __name__ == '__main__':
    app.run(debug=True)
