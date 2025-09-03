from gui import ClickCounterGUI

if __name__ == '__main__':
    try:
        app = ClickCounterGUI()
        app.run()
    except Exception as e:
        print(f'Error: {e}')
