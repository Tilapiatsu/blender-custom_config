
import bpy

def install_package(name):
    try:
        import site
        import os
        import sys
        user_site_packages = site.getusersitepackages()
        print('user_site_packages', user_site_packages)
        os.makedirs(user_site_packages, exist_ok = True)
        sys.path.append(user_site_packages) 

        __import__(name)
    except Exception as e:
        print(e)
        try:
            import site
            import os
            import sys
            user_site_packages = site.getusersitepackages()
            os.makedirs(user_site_packages, exist_ok = True)
            sys.path.append(user_site_packages)  

            print('installing package')
            if bpy.app.version < (2,91,0):
                python_binary = bpy.app.binary_path_python
            else:
                import sys
                python_binary = sys.executable

            import subprocess                
            try:
                print(python_binary, '-m', 'pip', 'install', name, "--user")
                subprocess.run([python_binary, '-m', 'pip', 'install', name, "--user"], check=True)                    
            except subprocess.CalledProcessError as e:
                print(e.output)

            __import__(name)
        except Exception as e2:
            return False
    return True

