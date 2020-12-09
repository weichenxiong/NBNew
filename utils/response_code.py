# coding:utf-8

class Code:
    OK                  = "0"
    DBERR               = "4001"
    NODATA              = "4002"
    DATAEXIST           = "4003"
    DATAERR             = "4004"
    SESSIONERR          = "4101"
    LOGINERR            = "4102"
    PARAMERR            = "4103"
    USERERR             = "4104"
    ROLEERR             = "4105"
    PWDERR              = "4106"
    REQERR              = "4201"
    IPERR               = "4202"
    THIRDERR            = "4301"
    IOERR               = "4302"
    SERVERERR           = "4500"
    UNKOWNERR           = "4501"

error_map = {
    Code.OK                    : u"成功",
    Code.DBERR                 : u"数据库查询错误",
    Code.NODATA                : u"无数据",
    Code.DATAEXIST             : u"数据已存在",
    Code.DATAERR               : u"数据错误",
    Code.SESSIONERR            : u"用户未登录",
    Code.LOGINERR              : u"用户登录失败",
    Code.PARAMERR              : u"参数错误",
    Code.USERERR               : u"用户不存在或未激活",
    Code.ROLEERR               : u"用户身份错误",
    Code.PWDERR                : u"密码错误",
    Code.REQERR                : u"非法请求或请求次数受限",
    Code.IPERR                 : u"IP受限",
    Code.THIRDERR              : u"第三方系统错误",
    Code.IOERR                 : u"文件读写错误",
    Code.SERVERERR             : u"内部错误",
    Code.UNKOWNERR             : u"未知错误",
}
