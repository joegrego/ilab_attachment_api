# ilab_attachment_api
How to use the Agilent iLab API to add an attachment to a request

This is an example Python3 program that demonstrates how to add an attachment to a request using the iLab API.

* Requires the installation of the "requests" python library. `pip install requests`, or use the requirements.txt file.
* You should update API_BASE below to your server.
* Requires an environment variable, defined below, that contains your API Bearer Token; update to work with your secrets.

To run:
```shell
pip install -r requirements.txt
export ILAB_API_TOKEN="YOUR-TOKEN-GOES-HERE"
python3 main.py -id 123456 -f ~/readme.txt -n "A Test Attachment" -v
```
You can also use the Service Request Name instead of the Service Reqeust ID. But to do that, you'll need to know your Core ID from iLab. (you probably do...)
```shell
python3 main.py -name 9876-ABC -c 1234 -f ~/readme.txt -n "Another Test Attachment" 
```
