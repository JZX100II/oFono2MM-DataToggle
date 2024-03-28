import os

async def logs_in_file(message, instance_of_sth = None):
        logs_dir = os.path.join('/var/lib/ofono2mm')
        logs_path = os.path.join(logs_dir, 'logs')

        with open(logs_path, 'a') as logs:
            if instance_of_sth:
                formatted_message = f"{message} - Instance details: {instance_of_sth} \n"
            else:
                formatted_message = f"{message} \n"

            logs.write(formatted_message)
