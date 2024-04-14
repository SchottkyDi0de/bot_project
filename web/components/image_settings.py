from nicegui import ui


with ui.header().classes(replace='row items-center') as header:
    ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=black')
    with ui.tabs() as tabs:
        ui.tab('Image Settings')
        ui.tab('Widget Settings')

with ui.footer(value=False) as footer:
    ui.label('Version 0.0.1 A')

with ui.left_drawer().classes('bg-blue-80') as left_drawer:
    ui.label('Side menu')

with ui.page_sticky(position='bottom-right', x_offset=20, y_offset=20):
    ui.button(on_click=footer.toggle, icon='help').props('fab')

with ui.tab_panels(tabs, value='A').classes('w-full'):
    with ui.tab_panel('Image Settings'):
        ui.label('Content of A')
    with ui.tab_panel('Widget Settings'):
        ui.label('Content of B')

ui.run()
