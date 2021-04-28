from lib.share import JR

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
import json,traceback
from main.models import User
from config.settings import UPLOAD_DIR
from datetime import datetime
from random import randint

class SignHandler:
    def handle(self,request):
        pd = json.loads(request.body)
        
        action = pd.get('action')
        
        request.pd = pd
        
        if action == 'signin':
            return self.signin(request)
        elif action == 'signout':
            return self.signout(request)
        else:
            return JR({'ret': 2, 'msg': 'action 参数错误'})
        
    def signin(self,request):
        
        # 从 HTTP POST 请求中获取用户名、密码参数
        userName = request.pd.get('username')
        passWord = request.pd.get('password')

        # 使用 Django auth 库里面的 方法校验用户名、密码
        user = authenticate(username=userName, password=passWord)
    
        # 如果能找到用户，并且密码正确
        if user is None:
            return JR({'ret': 1, 'msg': '用户名或者密码错误'})
        
        if not user.is_active:
            return JR({'ret': 0, 'msg': '用户已经被禁用'})
        
        login(request,user)

        return JR(
            {
                "ret":0,
                "usertype":user.usertype,
                "userid":user.id,
                "realname":user.realname
            }
        )
            
    def signout(self,request):
        # 使用登出方法
        logout(request)
        return JR({'ret': 0})
class AccountHandler:
    def handle(self,request):
        if request.method == 'GET':
            pd = request.GET
        else:
            pd = json.loads(request.body)
        
        request.pd = pd
        
        action = pd.get('action')
        
        if action == 'listbypage':
            return self.listbypage(request)
        elif action == 'addone':
            return self.addone(request)
        elif action == 'modifyone':
            return self.modifyone(request)
        elif action == 'deleteone':
            return self.deleteone(request)
        else:
            return JR({'ret': 2, 'msg': 'action 参数错误'})
        
    def addone(self,request):
        
        data = request.pd.get('data')
        
        ret = User.addone(data)
        
        return JR(ret)
    
    def listbypage(self,request):
        
        pagenum = int(request.pd.get('pagenum'))
        pagesize = int(request.pd.get('pagesize'))
        keywords = request.pd.get('keywords')
        
        ret = User.listbypage(pagenum,pagesize,keywords)
        
        return JR(ret)
    
    def modifyone(self,request):
        
        newdata = request.pd.get('newdata')
        oid = request.pd.get('id')
        
        ret = User.modifyone(oid,newdata)
        
        return JR(ret)

    def deleteone(self,request):
        
        oid = request.pd.get('id')
        
        ret = User.deleteone(oid)
        
        return JR(ret)

class UploadHandler:
    def handle(self,request):
        uploadFile = request.FILES['upload1']
        
        filetype = uploadFile.name.split('.')[-1]
        
        if filetype not in ['jpg','png']:
            return JR({'ret':430, 'msg':'只能上传 jpg png 文件'})
        
        if uploadFile.size > 10*1024*1024:
            return JR({'ret':431, 'msg':'只能上传小于10Mb的文件'})
        
        suffix = datetime.now().strftime('%Y%m%d%H%M%S_')+str(randint(0,999999))
        filename = f'{request.user.id}_{suffix}.{filetype}'
        
        #写入文件到静态文件访问区
        with open(f'{UPLOAD_DIR}/{filename}','wb') as f:
            #读取上传文件数据
            bytes = uploadFile.read()
            #写入文件
            f.write(bytes)
        
        return JR({'ret':0, 'url':f'/upload/{filename}'})