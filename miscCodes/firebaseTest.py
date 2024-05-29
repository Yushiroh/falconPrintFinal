import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

databaseURL = 'https://fileuploading-67153-default-rtdb.asia-southeast1.firebasedatabase.app' 

ticketValue = '-NvSCmNWdSZkeSG8nxKY'

cred = credentials.Certificate("fbaseKey1.json")
default_app = firebase_admin.initialize_app(cred, {
	'databaseURL':databaseURL
	})

ref = db.reference(f"/rfidData")

refChild = ref.child('F64C2ED4')



# refChild.set({'affiliation':"Adamson"})
# refChild.set({'studentNumber':201813457})
refChild.set({'studentName':"Franz Santos"})
# refChild.set({'credit':0})
# transactionStatus = ref.child("transactionStatus").get()

# print(transactionStatus)