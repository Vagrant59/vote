from urllib.parse import unquote

import xlwt
from six import BytesIO
from urllib.parse import quote
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import render, redirect

from polls.models import Subject, Teacher, User
from polls.captcha import Captcha
from polls.utils import gen_random_code, gen_md5_digest


def show_subjects(request: HttpRequest) -> HttpResponse:
    """渲染学科界面"""
    subjects = Subject.objects.all().order_by('no')
    return render(request, 'subjects.html', {
        'subjects': subjects
    })


def show_teachers(request):
    """渲染老师界面"""
    try:
        sno = int(request.GET.get('sno'))
        teachers = []
        if sno:
            subject = Subject.objects.only('name').get(no=sno)
            teachers = Teacher.objects.filter(subject=subject).order_by('no')
        return render(request, 'teachers.html', {
            'subject': subject,
            'teachers': teachers
        })
    except (ValueError, Subject.DoesNotExist):
        return redirect('/')


def praise_or_criticize(request: HttpRequest) -> HttpResponse:
    """渲染投票"""
    if request.session.get('userid'):
        try:
            tno = int(request.GET.get('tno'))
            teacher = Teacher.objects.get(no=tno)
            if request.path.startswith('/praise/'):
                teacher.good_count += 1
                count = teacher.good_count
            else:
                teacher.bad_count += 1
                count = teacher.bad_count
            teacher.save()
            # return redirect(f'/teachers/?sno={sno}')
            data = {'code': 20000, 'message': '投票成功', 'count': count}
        except (ValueError, Teacher.DoesNotExist):
            # return redirect('/')
            data = {'code': 20001, 'message': '投票失败'}
    else:
        data = {'code': 20002, 'message': '请先登录'}
        # return HttpResponse(json.dumps(data), content_type='application/json')
    return JsonResponse(data)


def get_captcha(request: HttpRequest) -> HttpResponse:
    """渲染验证码"""
    code = gen_random_code()
    request.session['captcha'] = code
    image_data = Captcha.instance().generate(code)
    return HttpResponse(image_data, content_type='image/png')


def login(request: HttpRequest) -> HttpResponse:
    """渲染登录界面"""
    hint = ''
    backurl = request.GET.get('backurl', '/')
    if request.method == 'POST':
        backurl = request.POST.get('backurl', '/')
        if backurl != '/':
            backurl = unquote(backurl)
        captchar_from_serv = request.session.get('captcha', '0')
        captchar_from_user = request.POST.get('captcha', '1')
        if captchar_from_serv.lower() == captchar_from_user.lower():
            username = request.POST.get('username')
            password = request.POST.get('password')
            if username and password:
                password = gen_md5_digest(password)
                user = User.objects.filter(username=username, password=password).first()
                if user:
                    request.session['userid'] = user.no
                    request.session['username'] = user.username
                    return redirect(backurl)
                else:
                    hint = '用户名或密码错误'
            else:
                hint = '请输入有效的用户名和密码'
        else:
            hint = '验证码有误，请重新输入'
    return render(request, 'login.html', {
        'hint': hint,
        'backurl': backurl,
    })


def logout(request: HttpRequest) -> HttpResponse:
    """渲染注销"""
    request.session.flush()
    return redirect('/')


def register(request: HttpRequest) -> HttpResponse:
    """渲染注册"""
    hint = ''
    if request.method == 'POST':
        agreement = request.POST.get('agreement')
        user = User()
        if agreement:
            user.username = request.POST.get('username')
            user.password = request.POST.get('password')
            user.tel = request.POST.get('tel')
            if user.username and user.password and user.tel:
                try:
                    user.password = gen_md5_digest(user.password)
                    user.save()
                    return redirect('/login/')
                except:
                    hint = '该用户名已被使用'
            else:
                hint = '请将注册信息填写完整'
        else:
            hint = '请勾选用户协议'
    return render(request, 'register.html', {'hint': hint})


def export_teachers_excel(request):
    # 创建工作簿
    wb = xlwt.Workbook()
    # 添加工作表
    sheet = wb.add_sheet('老师信息表')
    # 查询所有老师的信息
    queryset = Teacher.objects.all().select_related('subject')
    # 向Excel表单中写入表头
    colnames = ('姓名', '介绍', '好评数', '差评数', '学科')
    for index, name in enumerate(colnames):
        sheet.write(0, index, name)
    # 向单元格中写入老师的数据
    props = ('name', 'detail', 'good_count', 'bad_count', 'subject')
    for row, teacher in enumerate(queryset):
        for col, prop in enumerate(props):
            # getattr() 函数用于返回teacher对象中prop对应的属性值
            value = getattr(teacher, prop, '')
            # isinstance() 函数来判断一个对象是否是一个已知的类型，类似 type()
            if isinstance(value, Subject):
                value = value.name
            sheet.write(row + 1, col, value)
    # 保存Excel
    buffer = BytesIO()
    wb.save(buffer)
    # 将二进制数据写入响应的消息体中并设置MIME类型
    resp = HttpResponse(buffer.getvalue(), content_type='application/vnd.ms-excel')
    # 中文文件名需要处理成百分号编码
    filename = quote('老师.xls')
    # 通过响应头告知浏览器下载该文件以及对应的文件名
    resp['content-disposition'] = f'attachment; filename*=utf-8\'\'{filename}'
    return resp


def get_teachers_data(request):
    """渲染老师评价统计图"""
    queryset = Teacher.objects.all().only('name', 'good_count', 'bad_count')
    names = [teacher.name for teacher in queryset]
    good_counts = [teacher.good_count for teacher in queryset]
    bad_counts = [teacher.bad_count for teacher in queryset]
    return JsonResponse({'names': names, 'good': good_counts, 'bad': bad_counts})
