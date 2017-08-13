from distutils.core import setup

setup(
    name='pitrainer',
    version='0.2',
    packages=['tests', 'pi_trainer', 'pi_trainer.skip', 'pi_trainer.Accel', 'pi_trainer.config', 'pi_trainer.rumble',
              'pi_trainer.UDPComms', 'pi_trainer.DisplayHandler'],
    url='',
    license='',
    author='Richard-Kirby',
    author_email='richard.james.kirby@gmail.com',
    description='A virtual personal trainer on a Raspberry Pi'
)
