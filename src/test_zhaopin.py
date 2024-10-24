
import os
import qianfan

# 通过环境变量初始化认证信息
# 方式一：【推荐】使用安全认证AK/SK鉴权
# 替换下列示例中参数，安全认证Access Key替换your_iam_ak，Secret Key替换your_iam_sk，如何获取请查看https://cloud.baidu.com/doc/Reference/s/9jwvz2egb
os.environ["QIANFAN_ACCESS_KEY"] = "cd8b9ae5abc748c7a69066ab5c264376"
os.environ["QIANFAN_SECRET_KEY"] = "e384b45b9d974721a0f5d1c1e3dd22ab"

# 方式二：【不推荐】使用应用AK/SK鉴权
# 替换下列示例中参数，将应用API_Key、应用Secret key值替换为真实值
#os.environ["QIANFAN_AK"] = "应用API_Key"
#os.environ["QIANFAN_SK"] = "应用Secret_Key"

chat_comp = qianfan.ChatCompletion()

prompt = "你是一个解析者"
content = "请解析链接https://weixin.sogou.com/link?url=dn9a_-gY295K0Rci_xozVXfdMkSQTLW6cwJThYulHEtVjXrGTiVgSx-4yEwvX0yD4gijyifIIybiQWykYhd-51qXa8Fplpd9F2uHiuvRfHycyP9bL7pW2EBNRjcF0q7wiip1YpRp9fz_YCg_psJ0TfDxpWR0UXBplcR5AwGYDO_SVONxoXNgZeZCsYsvK7-AYDuHW36GRBXCahfyqB2DPZ4_XpVuLM5AvwNg6gH9-vLFjeTP5eLCMCwOq336FfnH_bQ4Y_uMhHVj3x9Nw6p-Fg..&type=2&query=%E8%BE%BD%E5%AE%81%E4%BA%BA%E6%89%8D%E6%8B%9B%E8%81%98%E4%BF%A1%E6%81%AF%E7%BD%91&token=7689161699F772CDE9ECCCDAEAA987A2EADD35366719B4E1&k=35&h=y 中的招聘对象和招聘专业"
# 指定特定模型
resp = chat_comp.do(model="ERNIE-Speed-128K", messages=[{
    "role": "user",
    "content": prompt+content
}])

print(resp["body"].get("result"))
