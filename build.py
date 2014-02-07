#!/usr/bin/python
#coding=utf-8

import os
import sys
import sh

config = 'config.json'
config_original = 'config.json.original'

assert os.path.isdir('catsup')
assert os.path.isdir('posts')
assert os.path.isfile(config_original)

## 安装 catsup ##
pwd = os.getcwd()

if (len(sys.argv) > 1) and \
    ((sys.argv[1] == '--not-install') or (sys.argv[1] == '-n')):
        pass
else:
    try:
        sh.cd('catsup')
        sh.python('setup.py', 'install')
        version = sh.catsup(version=True).replace(os.linesep, '')
        print u'Catsup 安装成功。当前版本：%s' % version
    except sh.ErrorReturnCode_1, message:
        print u'在安装 catsup 的时候发生了错误：'
        print message

    sh.cd(pwd)

## 获取主题列表 ##
ignore_dirs = ('catsup', 'posts', 'themes', 'demo', '.catsup-cache', '.git')
templates_list = []

for one in os.listdir('.'):
    if os.path.isdir(one) and not one in ignore_dirs:
        templates_list.append(one)

## 开始生成 ##
for theme_path in templates_list:
    if theme_path.startswith('catsup-theme-'):
        theme_name = theme_path[len('catsup-theme-'):]
    else:   theme_name = theme_path

    print u'开始为主题 %s 生成 Demo 页面。' % theme_name

    ## 生成配置文件 ##
    if os.path.isfile(config):
        os.remove(config)

    data = open(config_original).read()

    theme_vars = {}
    execfile(theme_path + os.sep + 'theme.py', theme_vars)

    if not theme_vars['vars'].get('github'):
        theme_vars['vars']['github'] = 'oyiadin'
    theme_vars['github'] = theme_vars['vars']['github']
    del theme_vars['vars']

    data = data % theme_vars

    with open(config, 'w') as f:
        f.write(data)
        f.close()

    ## 生成 Demo ##
    sh.catsup('install', theme_name)
    sh.catsup('build')
    
