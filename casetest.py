import subprocess  
  
# 添加新的cron任务  
new_cron_job = '0 2 * * * /usr/bin/python3 /path/to/your/script.py'  
  
# 列出当前cron任务  
current_jobs = subprocess.check_output(['crontab', '-l']).decode('utf-8')  
  
# 如果新任务不在列表中，则添加它  
if new_cron_job not in current_jobs:  
    # 注意：这里我们简单地通过管道将echo和crontab命令结合起来  
    # 在生产环境中，你应该更加小心地处理这种情况  
    subprocess.run(['(crontab -l 2>/dev/null; echo "{}") | crontab -'.format(new_cron_job)], shell=True)  
  
# 注意：上面的shell=True使用需要谨慎，因为它可能使你的代码容易受到shell注入攻击  
# 在可能的情况下，避免使用shell=True，而是使用列表形式的参数
