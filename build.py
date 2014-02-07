#!/usr/bin/python
#coding=utf-8

import os
import sys
import sh
import jinja2
import time

config = 'config.json'
config_original = 'config.json.original'
index = 'index.html'
repo_dir = '../catsup-themes.github.io/'

assert os.path.isdir('catsup')
assert os.path.isdir('posts')
assert os.path.isfile(config_original)

## 安装 catsup ##
pwd = os.getcwd()

if (len(sys.argv) > 1) and \
    ((sys.argv[1] == '--not-install') or (sys.argv[1] == '-n')):
        pass
else:
    print u'开始安装 Catsup。'

    try:
        sh.cd('catsup')
        sh.python('setup.py', 'install')
    except sh.ErrorReturnCode_1, message:
        print u'在安装 catsup 的时候发生了错误：'
        print message

    sh.cd(pwd)
version = sh.catsup(version=True).replace(os.linesep, '')
print u'当前 Catsup 版本：%s' % version

## 获取主题列表 ##
ignore_dirs = ('catsup', 'posts', 'themes', 'demo', '.catsup-cache', '.git')
templates_list = []
templates_name_list = []

for one in os.listdir('.'):
    if os.path.isdir(one) and not one in ignore_dirs:
        templates_list.append(one)

for template in templates_list:
    if template.startswith('catsup-theme-'):
        templates_name_list.append(
            (template, template[len('catsup-theme-'):])
        )
    else:
        templates_name_list.append(
            (template, template)
        )


## 开始生成 ##
for theme in templates_name_list:
    theme_path = theme[0]
    theme_name = theme[1]

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

time = time.time()

## 生成 demo/index.html ##
print u'开始生成主页。'

index_template = jinja2.Template(open(index).read())

if not os.path.isdir('demo'):   os.mkdir('demo')

with open('demo' + os.sep + index, 'w') as f:
    f.write(index_template.render(
        templates=templates_name_list,
        time=time,
        version=version ))
    f.close()

## 复制文件到 repo 内并上传 ##
print u'生成完毕；开始复制文件。'

sh.rm('-rf',
    os.path.join(repo_dir, 'index.html'), os.path.join(repo_dir, 'demo'))
sh.cp('demo/index.html', os.path.join(repo_dir, 'index.html'))
sh.cp('-r', 'demo/', os.path.join(repo_dir, 'demo'))
sh.git('add', '*')
sh.git('commit', '-am', 'update %s' % time)
sh.git('push')

print u'复制完毕；停止工作。'
