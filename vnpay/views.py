import hashlib
import hmac
import json
import urllib
import urllib.parse
import urllib.request
import random
import requests
from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.utils.http import urlquote
from rest_framework import viewsets
from rest_framework.decorators import action

from authentication.mixins import GetSerializerClassMixin
from base.message import error, success
from vnpay import settings
from vnpay.vnpay import vnpay


class VnpayViewSet(GetSerializerClassMixin, viewsets.ModelViewSet):
    def index(self, request):
        return render(request, "index.html", {"title": "Danh sách demo"})

    def hmacsha512(self, key, data):
        byteKey = key.encode('utf-8')
        byteData = data.encode('utf-8')
        return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest()

    def payment(self, request):
        if request.method == 'POST':
            # Process input data and build url payment
            form = request.data
            if form:
                order_type = form['orderType']
                order_id = form['orderId']
                amount = form['amount']
                order_desc = 'Thanh toan hoa don ' + datetime.now().strftime('%Y%m%d%H%M%S')
                ipaddr = self.get_client_ip(request)
                # Build URL Payment
                vnp = vnpay()
                vnp.requestData['vnp_Version'] = '2.1.0'
                vnp.requestData['vnp_Command'] = 'pay'
                vnp.requestData['vnp_TmnCode'] = settings.VNPAY_TMN_CODE
                vnp.requestData['vnp_Amount'] = amount
                vnp.requestData['vnp_CurrCode'] = 'VND'
                vnp.requestData['vnp_TxnRef'] = order_id
                vnp.requestData['vnp_OrderInfo'] = order_desc
                vnp.requestData['vnp_OrderType'] = order_type
                vnp.requestData['vnp_Locale'] = 'vn'
                vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')  # 20150410063022
                vnp.requestData['vnp_IpAddr'] = ipaddr
                vnp.requestData['vnp_ReturnUrl'] = settings.VNPAY_RETURN_URL
                vnpay_payment_url = vnp.get_payment_url(settings.VNPAY_PAYMENT_URL, settings.VNPAY_HASH_SECRET_KEY)
            else:
                return error(data="Form không đúng định dạng")
            print(vnpay_payment_url)
            return success(data=vnpay_payment_url)
        else:
            return error(data="Method phải là POST")

    def payment_ipn(self, request):
        inputData = request.GET
        if inputData:
            vnp = vnpay()
            vnp.responseData = inputData.dict()
            order_id = inputData['vnp_TxnRef']
            amount = inputData['vnp_Amount']
            order_desc = inputData['vnp_OrderInfo']
            vnp_TransactionNo = inputData['vnp_TransactionNo']
            vnp_ResponseCode = inputData['vnp_ResponseCode']
            vnp_TmnCode = inputData['vnp_TmnCode']
            vnp_PayDate = inputData['vnp_PayDate']
            vnp_BankCode = inputData['vnp_BankCode']
            vnp_CardType = inputData['vnp_CardType']
            if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
                # Check & Update Order Status in your Database
                # Your code here
                firstTimeUpdate = True
                totalamount = True
                if totalamount:
                    if firstTimeUpdate:
                        if vnp_ResponseCode == '00':
                            print('Payment Success. Your code implement here')
                        else:
                            print('Payment Error. Your code implement here')

                        # Return VNPAY: Merchant update success
                        result = JsonResponse({'RspCode': '00', 'Message': 'Confirm Success'})
                    else:
                        # Already Update
                        result = JsonResponse({'RspCode': '02', 'Message': 'Order Already Update'})
                else:
                    # invalid amount
                    result = JsonResponse({'RspCode': '04', 'Message': 'invalid amount'})
            else:
                # Invalid Signature
                result = JsonResponse({'RspCode': '97', 'Message': 'Invalid Signature'})
        else:
            result = JsonResponse({'RspCode': '99', 'Message': 'Invalid request'})

        return result

    def payment_return(self, request):
        inputData = request.GET
        if inputData:
            vnp = vnpay()
            vnp.responseData = inputData.dict()
            order_id = inputData['vnp_TxnRef']
            amount = int(inputData['vnp_Amount']) / 100
            order_desc = inputData['vnp_OrderInfo']
            vnp_TransactionNo = inputData['vnp_TransactionNo']
            vnp_ResponseCode = inputData['vnp_ResponseCode']
            vnp_TmnCode = inputData['vnp_TmnCode']
            vnp_PayDate = inputData['vnp_PayDate']
            vnp_BankCode = inputData['vnp_BankCode']
            vnp_CardType = inputData['vnp_CardType']
            if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
                if vnp_ResponseCode == "00":
                    return render(request, "payment_return.html", {"title": "Kết quả thanh toán",
                                                                   "result": "Thành công", "order_id": order_id,
                                                                   "amount": amount,
                                                                   "order_desc": order_desc,
                                                                   "vnp_TransactionNo": vnp_TransactionNo,
                                                                   "vnp_ResponseCode": vnp_ResponseCode})
                else:
                    return render(request, "payment_return.html", {"title": "Kết quả thanh toán",
                                                                   "result": "Lỗi", "order_id": order_id,
                                                                   "amount": amount,
                                                                   "order_desc": order_desc,
                                                                   "vnp_TransactionNo": vnp_TransactionNo,
                                                                   "vnp_ResponseCode": vnp_ResponseCode})
            else:
                return render(request, "payment_return.html",
                              {"title": "Kết quả thanh toán", "result": "Lỗi", "order_id": order_id, "amount": amount,
                               "order_desc": order_desc, "vnp_TransactionNo": vnp_TransactionNo,
                               "vnp_ResponseCode": vnp_ResponseCode, "msg": "Sai checksum"})
        else:
            return render(request, "payment_return.html", {"title": "Kết quả thanh toán", "result": ""})

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    n = random.randint(10**11, 10**12 - 1)
    n_str = str(n)
    while len(n_str) < 12:
        n_str = '0' + n_str


    def query(self, request):
        if request.method == 'GET':
            return render(request, "query.html", {"title": "Kiểm tra kết quả giao dịch"})

        url = settings.VNPAY_API_URL
        secret_key = settings.VNPAY_HASH_SECRET_KEY
        vnp_TmnCode = settings.VNPAY_TMN_CODE
        vnp_Version = '2.1.0'

        vnp_RequestId = self.n_str
        vnp_Command = 'querydr'
        vnp_TxnRef = request.POST['order_id']
        vnp_OrderInfo = 'kiem tra gd'
        vnp_TransactionDate = request.POST['trans_date']
        vnp_CreateDate = datetime.now().strftime('%Y%m%d%H%M%S')
        vnp_IpAddr = self.get_client_ip(request)

        hash_data = "|".join([
            vnp_RequestId, vnp_Version, vnp_Command, vnp_TmnCode,
            vnp_TxnRef, vnp_TransactionDate, vnp_CreateDate,
            vnp_IpAddr, vnp_OrderInfo
        ])

        secure_hash = hmac.new(secret_key.encode(), hash_data.encode(), hashlib.sha512).hexdigest()

        data = {
            "vnp_RequestId": vnp_RequestId,
            "vnp_TmnCode": vnp_TmnCode,
            "vnp_Command": vnp_Command,
            "vnp_TxnRef": vnp_TxnRef,
            "vnp_OrderInfo": vnp_OrderInfo,
            "vnp_TransactionDate": vnp_TransactionDate,
            "vnp_CreateDate": vnp_CreateDate,
            "vnp_IpAddr": vnp_IpAddr,
            "vnp_Version": vnp_Version,
            "vnp_SecureHash": secure_hash
        }

        headers = {"Content-Type": "application/json"}

        response = requests.post(url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            response_json = json.loads(response.text)
        else:
            response_json = {"error": f"Request failed with status code: {response.status_code}"}

        return render(request, "query.html", {"title": "Kiểm tra kết quả giao dịch", "response_json": response_json})

    def refund(self, request):
        if request.method == 'GET':
            return render(request, "refund.html", {"title": "Hoàn tiền giao dịch"})

        url = settings.VNPAY_API_URL
        secret_key = settings.VNPAY_HASH_SECRET_KEY
        vnp_TmnCode = settings.VNPAY_TMN_CODE
        vnp_RequestId = self.n_str
        vnp_Version = '2.1.0'
        vnp_Command = 'refund'
        vnp_TransactionType = request.POST['TransactionType']
        vnp_TxnRef = request.POST['order_id']
        vnp_Amount = request.POST['amount']
        vnp_OrderInfo = request.POST['order_desc']
        vnp_TransactionNo = '0'
        vnp_TransactionDate = request.POST['trans_date']
        vnp_CreateDate = datetime.now().strftime('%Y%m%d%H%M%S')
        vnp_CreateBy = 'user01'
        vnp_IpAddr = self.get_client_ip(request)

        hash_data = "|".join([
            vnp_RequestId, vnp_Version, vnp_Command, vnp_TmnCode, vnp_TransactionType, vnp_TxnRef,
            vnp_Amount, vnp_TransactionNo, vnp_TransactionDate, vnp_CreateBy, vnp_CreateDate,
            vnp_IpAddr, vnp_OrderInfo
        ])

        secure_hash = hmac.new(secret_key.encode(), hash_data.encode(), hashlib.sha512).hexdigest()

        data = {
            "vnp_RequestId": vnp_RequestId,
            "vnp_TmnCode": vnp_TmnCode,
            "vnp_Command": vnp_Command,
            "vnp_TxnRef": vnp_TxnRef,
            "vnp_Amount": vnp_Amount,
            "vnp_OrderInfo": vnp_OrderInfo,
            "vnp_TransactionDate": vnp_TransactionDate,
            "vnp_CreateDate": vnp_CreateDate,
            "vnp_IpAddr": vnp_IpAddr,
            "vnp_TransactionType": vnp_TransactionType,
            "vnp_TransactionNo": vnp_TransactionNo,
            "vnp_CreateBy": vnp_CreateBy,
            "vnp_Version": vnp_Version,
            "vnp_SecureHash": secure_hash
        }

        headers = {"Content-Type": "application/json"}

        response = requests.post(url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            response_json = json.loads(response.text)
        else:
            response_json = {"error": f"Request failed with status code: {response.status_code}"}

        return render(request, "refund.html", {"title": "Kết quả hoàn tiền giao dịch", "response_json": response_json})