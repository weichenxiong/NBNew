from qiniu import Auth, put_file, etag,put_data
import qiniu.config

#需要填写你的 Access Key 和 Secret Key
access_key = 'nBU58RaZgAhGSTrQTVS4Ly7omjtcin-6EKhAlXuq'
secret_key = 'AQn6hcDZKYrESqxbGq9-7Tl0kHGxhy07txx9Dw89'

def image_storage(image_data):
    #构建鉴权对象
    q = Auth(access_key, secret_key)

    #要上传的空间
    bucket_name = 'newstorage'

    #上传到七牛后保存的文件名,如果不指定,那么名字由七牛云维护
    # key = 'haha.png'
    key = None

    #生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, 3600)

    #要上传文件的本地路径
    # localfile = './44.jpg'

    # ret, info = put_file(token, key, localfile)
    ret, info = put_data(token, key, image_data)

    #处理上传的结果,如果上传成功,返回图片名称,否则返回None
    if info.status_code == 200:
        return ret.get("key")
    else:
        return None

#用来测试图片上传的
if __name__ == '__main__':

    #使用with测试,可以自动关闭流
    with open('./44.jpg','rb') as f:
        image_storage(f.read())