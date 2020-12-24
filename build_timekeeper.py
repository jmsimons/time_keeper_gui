from PyInstaller.__main__ import run


# Define build info #
package_name = 'Time-Keeper'
run_script = 'run.py'
flags = ['--clean', '--windowed', '--onefile']
add_data = [
    './export/:./export/',
    # './LICENSE:.',
    # './README.md:.',
    ]
add_binary = []


# Compile build info #
build_info = ['--name={}'.format(package_name), *flags, *['--add-data=' + i for i in add_data], *['--add-binary=' + i for i in add_binary], run_script]


# Run build #
if __name__ == '__main__':
    for i in build_info: print(i)
    run(build_info)