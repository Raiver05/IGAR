import pygame
import os
import copy
import tkinter as tk
from tkinter import filedialog
import random
from datetime import datetime
import ctypes
import ctypes.wintypes as wt
import math

# region Pygame & Display Initialization
pygame.init()

monitor_info = pygame.display.Info()																	# Pantalla Configuracion
screen_x : int = monitor_info.current_w
screen_y : int = monitor_info.current_h
rect_x : int = 8
rect_y : int = 16
screen : pygame.Surface = pygame.display.set_mode((screen_x, screen_y), pygame.NOFRAME)
icon = pygame.image.load("IGAR_data/IGAR.png")
pygame.display.set_icon(icon)
pygame.display.set_caption(" ")
																										
pygame.scrap.init()																						# Portapapeles Modulos Necesarios
pygame.scrap.set_mode(pygame.SCRAP_CLIPBOARD)
 
font_name : str = "IGAR_data/IGAR.ttf"															# Fuente
font = pygame.font.Font(font_name, 16)
constant_font = pygame.font.Font(font_name , 16)
# endregion Pygame & Display Initialization
# region vars

visible_cols = screen.get_width() // rect_x
visible_rows = screen.get_height() // rect_y
cols : int = screen_x // rect_x
rows : int = screen_y // rect_y
show_grid : bool = False
 
highlight_timer : int | None = None
highlight_state : int = 1
selected_cell: tuple[int, int] | None = None
first_selected_cell: tuple[int, int] | None = None
last_selected_cell: tuple[int, int] | None = None
selected_grid : list[tuple[int, int]] = []
grids: list[list[list[str]]] = []
grid : list[list[int | str]] = [[" " for y in range(rows)] for x in range(cols)]
current_grid : int = 0
max_x : int = 0
min_x : int = 0
max_y : int = 0
min_y : int = 0
 
last_export_path: str | None = None
current_file_path : str | None = None
 
text_cache : dict[str, pygame.Surface] = {}
 
needs_redraw : bool = True
 
key_repeat_delay : int = 500
key_repeat_interval : int = 30
pygame.key.set_repeat(key_repeat_delay, key_repeat_interval)
 
is_fullscreen : bool = True
windowed_size : tuple[int, int] = (screen_x // 2, screen_y // 2)
windowed_pos : tuple[int, int] = ((screen_x - windowed_size[0]) // 2, (screen_y - windowed_size[1]) // 2)

visible_ui : bool = True
saved : bool = False
confirm_exit : bool = False
confirm_new_grid : bool = False
igar_keyboard_shortcuts : bool = False
 
night_theme : bool = True
chars_color : tuple[int, int, int] = (255, 255, 255)
background_color : tuple[int, int, int] = (0, 0, 0)
 
temporal_grid : list[list[tuple[int, int]]]
temporal_line : list[tuple[int, int]]
h_flipped_chars : list[tuple[str, str]] = [("/", "\\"), ("4", "F"), ("d", "b"), ("J", "L"), ("`", "´")]
v_flipped_chars : list[tuple[str, str]] = [("/", "\\"), (".", "˙"), ("_", "~"), ('"', "₊"), ("J", "4"), ("L", "F")]
 
free_selection : list[tuple[int, int]] = []

matrix_grid : list[list[str]] = [[" " for y in range(rows)] for x in range(cols)]
matrix_mode : bool = False
matrix_start_time : int = 0
matrix_delay : int = 0
matrix_drops : list = []
drop_collision : bool = False

drawing_mode : bool = False
past_mouse_pos : list[str] = [0,0]

obj_grid : list[list[str]] = [[" " for y in range(rows)] for x in range(cols)]
obj_mode : bool = False
obj_cache: dict[str, tuple[list[list[float]], list[list[int]]]] = {}
obj_degree : int = 0
obj_last_render = pygame.time.get_ticks()
obj_free_selection : list[tuple[int, int]] = []

ui_grid : list[list[str]] = [[" " for y in range(rows)] for x in range(cols)]
current_zoom : int = 0

dvd_grid : list[list[str]] = [[" " for y in range(rows)] for x in range(cols)]
dvd_mode : bool = False
dvd_delay : int = 0
dvd_start_time : int = 0
dvd_exists : bool = False
dvd_art : list[str] = [
    " !IIII?  ₊gGGGGGGG.     AAAARRRRRRRRRbo.",
    "  ]I]   oGGª˙  ״IGG    AAAAA         \"RR",
    "  HI|  dGGª     ªªª   AA˙ AA   RRR   ₊RR",
    "  HH   gGG   GGggo   AA˙  AA  ]RRRRRRRª ",
    " |IH   GGg    ₊dGª  gAAAAAAA  ]RR   RRR ",
    " III   ªGGG₈₈ggGI  gAA    AA .RRR    RRR",
    "¿III¡   ªGGGª˙oP  oAA     AA :ÑR|     RR",
    "₊₊₊₊₊₊……ooogggggo------oggggg……………₊₊₊₊₊ ",
    " ˙˙˙˙˙״״״״״ªªªªª״------״ªªªªªªªª״״˙˙˙˙˙˙"
]
# region user32

user32 = ctypes.windll.user32

user32.GetForegroundWindow.restype = wt.HWND
user32.GetForegroundWindow.argtypes = []

window_visible : bool = True
window_covered : bool = False
window_focused : bool = True
visibility_check_timer : int = 0
visibility_check_interval : int = 500
window_topmost : bool = False

user32.SystemParametersInfoW.restype = wt.BOOL
user32.SystemParametersInfoW.argtypes = [wt.UINT, wt.UINT, ctypes.c_void_p, wt.UINT]
SPI_GETWORKAREA = 0x0030

SWP_NOSIZE = 0x0001
SWP_NOZORDER = 0x0004
SWP_NOACTIVATE = 0x0010

user32.SetWindowPos.restype = wt.BOOL
user32.SetWindowPos.argtypes = [wt.HWND, wt.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wt.UINT]

user32.GetClientRect.restype = wt.BOOL
user32.GetClientRect.argtypes = [wt.HWND, ctypes.POINTER(wt.RECT)]
SW_RESTORE = 9

user32.IsZoomed.restype = wt.BOOL
user32.IsZoomed.argtypes = [wt.HWND]

user32.ShowWindow.restype = wt.BOOL
user32.ShowWindow.argtypes = [wt.HWND, ctypes.c_int]

user32.MonitorFromWindow.restype = wt.HANDLE
user32.MonitorFromWindow.argtypes = [wt.HWND, wt.DWORD]

class MONITORINFO(ctypes.Structure):
	_fields_ = [("cbSize", wt.DWORD), ("rcMonitor", wt.RECT), ("rcWork", wt.RECT), ("dwFlags", wt.DWORD)]

user32.GetMonitorInfoW.restype = wt.BOOL
user32.GetMonitorInfoW.argtypes = [wt.HANDLE, ctypes.POINTER(MONITORINFO)]

MONITOR_DEFAULTTONEAREST = 2

user32.GetClassNameW.restype = ctypes.c_int
user32.GetClassNameW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]

SWP_NOMOVE = 0x0002
HWND_TOPMOST = -1
HWND_NOTOPMOST = -2
# endregion user32
# endregion vars
# region funcs
# region Win32

def restore_if_maximized() -> None:
	hwnd = pygame.display.get_wm_info()["window"]
	if user32.IsZoomed(hwnd):
		user32.ShowWindow(hwnd, SW_RESTORE)
def move_window(x: int, y: int) -> None:
	hwnd = pygame.display.get_wm_info()["window"]
	user32.SetWindowPos(hwnd, 0, x, y, 0, 0, SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE)

def get_window_geometry() -> tuple[int, int, int, int]:
	hwnd = pygame.display.get_wm_info()["window"]
	window_rect = wt.RECT()
	client_rect = wt.RECT()
	user32.GetWindowRect(hwnd, ctypes.byref(window_rect))
	user32.GetClientRect(hwnd, ctypes.byref(client_rect))
	return (window_rect.left, window_rect.top, client_rect.right, client_rect.bottom)

def get_monitor_rect() -> wt.RECT:
	hwnd = pygame.display.get_wm_info()["window"]
	hmonitor = user32.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)
	info = MONITORINFO()
	info.cbSize = ctypes.sizeof(MONITORINFO)
	user32.GetMonitorInfoW(hmonitor, ctypes.byref(info))
	return info.rcMonitor

def get_work_area() -> wt.RECT:
	hwnd = pygame.display.get_wm_info()["window"]
	hmonitor = user32.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)
	info = MONITORINFO()
	info.cbSize = ctypes.sizeof(MONITORINFO)
	user32.GetMonitorInfoW(hmonitor, ctypes.byref(info))
	return info.rcWork

def is_desktop_fully_covered() -> bool:
	if window_focused or window_topmost:
		return False
	fg_hwnd = user32.GetForegroundWindow()
	if fg_hwnd == 0:
		return False
	class_name = ctypes.create_unicode_buffer(256)
	user32.GetClassNameW(fg_hwnd, class_name, 256)
	if class_name.value in ("Progman", "WorkerW"):
		return False
	rect = wt.RECT()
	user32.GetWindowRect(fg_hwnd, ctypes.byref(rect))
	work_area = get_work_area()
	return rect.left <= work_area.left and rect.top <= work_area.top and rect.right >= work_area.right and rect.bottom >= work_area.bottom

def toggle_topmost() -> None:
	global window_topmost
	window_topmost = not window_topmost
	hwnd = pygame.display.get_wm_info()["window"]
	if window_topmost:
		user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
	else:
		user32.SetWindowPos(hwnd, HWND_NOTOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)

def restore_focus():
	pygame.event.pump()
	pygame.display.get_surface()
	pygame.event.post(pygame.event.Event(pygame.ACTIVEEVENT, gain=1, state=1))

# endregion Win32
# region Magic Wand
def magic_wand(x : int, y : int, grid : list[list[str]] = None, selection : list[tuple[int, int]] = None):
	if grid is None:
		grid = globals()['grid']
	if selection is None:
		selection = free_selection
	magic_char : str = grid[x][y]
	get_adjacent_cells(x, y, grid , selection, magic_char)

def get_adjacent_cells(x: int, y: int, grid : list[list[str]] = None , selection: list[tuple[int, int]] = None, char: str = " "):
	if grid is None:
		grid = globals()['grid']
	if selection is None:
		selection = free_selection

	visited = set()
	to_process = [(x, y)]
	visited.add((x, y))

	while to_process:
		new_cells = []
		for current_cell in to_process:
			adjacent_cells = [
				(current_cell[0] + 1, current_cell[1]),
				(current_cell[0] - 1, current_cell[1]),
				(current_cell[0], current_cell[1] + 1),
				(current_cell[0], current_cell[1] - 1)
			]
			for adj_cell in adjacent_cells:
				if (0 <= adj_cell[0] < cols and 0 <= adj_cell[1] < rows and 
					adj_cell not in visited and 
					grid[adj_cell[0]][adj_cell[1]] == char):
					visited.add(adj_cell)
					new_cells.append(adj_cell)
		to_process = new_cells

	selection[:] = list(visited)

def absolute_magic_wand(x : int, y : int, grid : list[list[str]] = None, selection : list[tuple[int, int]] = None):
	if grid is None:
		grid = globals()['grid']
	if selection is None:
		selection = free_selection
	selection.clear()
	magic_char : str = grid[x][y]
	for a in range(cols):
		for b in range(rows):
			if grid[a][b] == magic_char:
				selection.append((a, b))

# endregion Magic Wand
# region Record
def grid_changed():															# Grid Changed
	global grids, current_grid, saved
	if grid == grids[current_grid]:
		return
	if current_grid + 1 < len(grids):
		grids = grids[:current_grid + 1]
	grids.append(copy.deepcopy(grid))
	current_grid = len(grids) - 1
	saved = False
def undo() -> None:															# Deshacer
	global grid, current_grid, needs_redraw, saved
	if current_grid > 0:
		current_grid -= 1
		grid[:] = copy.deepcopy(grids[current_grid])
		needs_redraw = True
		saved = False
	else:
		pass
def redo() -> None:															# Rehacer
	global grid, current_grid, needs_redraw, saved
	if current_grid < len(grids) - 1: 
		current_grid += 1
		grid[:] = copy.deepcopy(grids[current_grid])
		needs_redraw = True
		saved = False
	else:
		pass
# endregion Record
# region Files

def close_igar(event = None):
	global running, saved, confirm_exit
	if event:
		if event.type == pygame.QUIT or event.key == pygame.K_F8:
			if saved == True: 
				running = False
			elif confirm_exit:
				running = False
			else:
				confirm_exit = True
		elif event.key == pygame.K_ESCAPE:
			if confirm_exit:
				confirm_exit = False
def new_grid():																# Nueva Grilla
	global saved, confirm_new_grid, needs_redraw, current_file_path, last_export_path
	if saved == True: 
		for x in range(cols):
			for y in range(rows):
				grid[x][y] = " "
		needs_redraw = True	
		grid_changed()
		current_file_path = None
		last_export_path = None
	elif confirm_new_grid:
		if event.mod & pygame.KMOD_CTRL and event.key == pygame.K_n:
			for x in range(cols):
				for y in range(rows):
					grid[x][y] = " "
			needs_redraw = True
			grid_changed()
			confirm_new_grid = False
			current_file_path = None
			last_export_path = None
		elif event.key == pygame.K_ESCAPE:
			confirm_new_grid = False
	else:
		if event.key == pygame.K_n:
			confirm_new_grid = True
def save_grid():															# Guarda Grilla
	global current_file_path, saved
	if current_file_path == None:
		save_grid_as()
		return
	with open(current_file_path, "w", encoding="utf-8") as f:
		for y in range(rows):
			linea = "".join(str(grid[x][y]) for x in range(cols))
			f.write(linea + "\n")
	saved = True
def save_grid_as():															# Guarda Grilla Como
	global current_file_path
	root = tk.Tk()
	root.withdraw()
	file_path = filedialog.asksaveasfilename(
		defaultextension=".txt",
		filetypes=[("Text files", "*.txt")],
		title="Save as..."
	)
	root.destroy()
	restore_focus()
	if file_path:
		current_file_path = file_path
		save_grid()
def load_grid():															# Abre Grilla
	global current_file_path, last_export_path, needs_redraw, saved
	root = tk.Tk()
	root.withdraw()
	file_path = filedialog.askopenfilename(
		filetypes=[("Text files", "*.txt")],
		title="Open..."
	)
	root.destroy()
	restore_focus()
	if file_path:
		current_file_path = file_path
		last_export_path = None
		with open(file_path, "r", encoding="utf-8") as f:
			lines = f.readlines()
		for y in range(min(rows, len(lines))):
			for x in range(min(cols, len(lines[y].rstrip("\n")))):
				grid[x][y] = lines[y][x]
			for x in range(len(lines[y].rstrip("\n")), cols):
				grid[x][y] = " "
		for y in range(len(lines), rows):
			for x in range(cols):
				grid[x][y] = " "
		grid_changed()
		needs_redraw = True
		saved = True
def save_canvas_as_png(surface: pygame.Surface, save_path: str) -> None:	# Crea PNG
	pygame.image.save(surface, save_path)
def export_canvas(surface: pygame.Surface) -> str | None:					# Exporta PNG
	global selected_grid, free_selection
	
	selection = selected_grid + free_selection
	
	# Si hay selección, exportar solo esa área
	if selection:
		min_y = min(cell[1] for cell in selection)
		max_y = max(cell[1] for cell in selection)
		min_x = min(cell[0] for cell in selection)
		max_x = max(cell[0] for cell in selection)
		
		width = (max_x - min_x + 1) * rect_x
		height = (max_y - min_y + 1) * rect_y
		
		temp_surface = pygame.Surface((width, height))
		temp_surface.fill(background_color)
		
		for x in range(min_x, max_x + 1):
			for y in range(min_y, max_y + 1):
				cell = grid[x][y]
				if isinstance(cell, str) and cell != "" and cell != " ":
					text_surf = get_text_surface(cell)
					pos_x = (x - min_x) * rect_x
					pos_y = (y - min_y) * rect_y
					temp_surface.blit(text_surf, (pos_x, pos_y))
		
		export_surface = temp_surface
	else:
		export_surface = surface
	
	root = tk.Tk()
	root.withdraw()
	file_path: str = filedialog.asksaveasfilename(
		defaultextension=".png",
		filetypes=[("Imagen PNG", "*.png")],
		title="Exportar canvas como PNG"
	)
	root.destroy()
	restore_focus()
 
	if file_path:
		save_canvas_as_png(export_surface, file_path)
		return file_path
	return None

# endregion Files
# region UI

def handle_ui():
	global saved, max_x, min_x, max_y, min_y
	if not visible_ui:
		return

	visible_cols = screen.get_width() // rect_x
	visible_rows = screen.get_height() // rect_y

	for x in range(cols):
		for y in range(rows):
			ui_grid[x][y] = " "

	last_row = visible_rows - 1

	if current_file_path:
		filename = os.path.basename(current_file_path)
	else:
		filename = "-"
	
	star = "*" if not saved else ""
	pygame.display.set_caption(filename + star)

	coords_text = ""
	if selected_cell is not None:
		coords_text += f"({selected_cell[0]},{selected_cell[1]})"
	if selected_grid != []:
		if coords_text:
			coords_text += "   "
		coords_text += f"{max_x - min_x + 1}x{max_y - min_y + 1}"

	F1_message = "Press F1 to show/hide keyboard shortcuts"
	F1_message = ""
	F1_padded = f" {F1_message} "
	start_x_f1 = (visible_cols - len(F1_padded)) // 2

	max_filename_len = 20
	available_space = start_x_f1 - 4

	if available_space < max_filename_len:
		max_filename_len = available_space

	if max_filename_len <= 0:
		display_name = ""
	elif len(filename) > max_filename_len:
		if max_filename_len > 3:
			display_name = filename[:max_filename_len - 3] + "..." + star
		else:
			display_name = filename[:max_filename_len] + star
	else:
		display_name = filename + star

	if display_name:
		display_padded = f" {display_name} "
		for i, char in enumerate(display_padded):
			if 0 <= i < visible_cols:
				pygame.draw.rect(screen, background_color, (i * rect_x, last_row * rect_y, rect_x, rect_y))
				ui_grid[i][last_row] = char
		name_end_x = len(display_padded)
	else:
		name_end_x = 0

	if coords_text:
		coords_padded = f" {coords_text} "
		coords_len = len(coords_padded)
		space_between = start_x_f1 - name_end_x
		start_x_coords = name_end_x + (space_between - coords_len) // 2
		
		if start_x_coords < name_end_x:
			start_x_coords = name_end_x
			
		for i, char in enumerate(coords_padded):
			pos_x = start_x_coords + i
			if pos_x < start_x_f1 and 0 <= pos_x < visible_cols:
				pygame.draw.rect(screen, background_color, (pos_x * rect_x, last_row * rect_y, rect_x, rect_y))
				ui_grid[pos_x][last_row] = char

	for i, char in enumerate(F1_padded):
		pos_x = start_x_f1 + i
		if 0 <= pos_x < visible_cols:
			pygame.draw.rect(screen, background_color, (pos_x * rect_x, last_row * rect_y, rect_x, rect_y))
			ui_grid[pos_x][last_row] = char

	time_str = hora.strftime("%H:%M")
	time_padded = f" {time_str} "
	start_x_time = visible_cols - len(time_padded)
	for i, char in enumerate(time_padded):
		pos_x = start_x_time + i
		if 0 <= pos_x < visible_cols:
			pygame.draw.rect(screen, background_color, (pos_x * rect_x, last_row * rect_y, rect_x, rect_y))
			ui_grid[pos_x][last_row] = char
	
def draw_igar_keyboard_shortcuts():
	if not igar_keyboard_shortcuts:
		return
	shortcuts_lines = [
		"        IGAR Keyboard Shortcuts",
		"",
		"• F1 - Toggle IGAR Keyboard Shortcuts",
		"",
		"• Ctrl + N - New Grid",
		"• Ctrl + Shift + S - Save Grid As",
		"• Ctrl + S - Save Grid",
		"• Ctrl + Shift + E - Export PNG Grid As",
		"• Ctrl + E - Export PNG Grid",
		"• Ctrl + O - Open Grid",
		"",
		"• Ctrl + Z - Undo",
		"• Ctrl + Y - Redo",
		"",
		"• Ctrl + Shift + H - Flip Selection Horizontally",
		"• Ctrl + Shift + V - Flip Selection Vertically",
		"• Ctrl + Shift + W - Absolute Magic Wand",
		"• Ctrl + W - Magic Wand",
		"• Ctrl + T - Toggle Theme",
		"• Ctrl + V - Paste",
		"• Ctrl + C - Copy",
		"• Ctrl + X - Cut",
		"",
		"• Shift + Arrows - Select Rectangle Grid",
		"• Ctrl + 1,2,3,...,',¿ - Special Characters ",
		"• Ctrl + Arrows - Move Cells",
		"• Ctrl + G - Toggle Grid Visibility",
		"• Ctrl + D - Deselect Grid",
		"• Ctrl + R - Randomize($,#,&,@)",
		"",
		"• Ctrl + F - Toggle UI",
		"• F8 - Close IGAR",
		"• F11 - Toggle Fullscreen"
	]
	# Calcular tamaño
	line_height = constant_font.get_height()
	max_width = max(constant_font.size(line)[0] for line in shortcuts_lines)
	total_height = len(shortcuts_lines) * line_height
	padding = 20
	# Rectángulo
	box_rect = pygame.Rect(0, 0, max_width + padding * 2, total_height + padding * 2)
	box_rect.center = (screen.get_width() // 2, screen.get_height() // 2)
	pygame.draw.rect(screen, background_color, box_rect)
	# Renderizar y dibujar líneas
	start_y = box_rect.top + padding
	for i, line in enumerate(shortcuts_lines):
		text = constant_font.render(line, True, chars_color)
		screen.blit(text, (box_rect.left + padding, start_y + i * line_height))

def get_text_surface(char: str) -> pygame.Surface:
	if char not in text_cache:
		text_cache[char] = font.render(char, True, chars_color)
	return text_cache[char]

def get_text_length(text : str):
	l = 32
	for i in (text):
		l += 8
	return l

def draw_popup_message(message : str):
	box_rect = pygame.Rect(0, 0, get_text_length(message), 48)
	box_rect.center = (screen.get_width() // 2, screen.get_height() // 2)
	pygame.draw.rect(screen, background_color, box_rect)
	exit_text = constant_font.render(message, True, chars_color)
	screen.blit(exit_text, exit_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2)))

# endregion UI
# region Grid
def calculate_selection_limits():
	global min_x, max_x, min_y, max_y
	if selected_grid != []:
		min_x = min(cell[0] for cell in selected_grid)
		max_x = max(cell[0] for cell in selected_grid)
		min_y = min(cell[1] for cell in selected_grid)
		max_y = max(cell[1] for cell in selected_grid)
	else: 
		if selected_cell != None:
			min_x = selected_cell[0]
			max_x = selected_cell[0]
			min_y = selected_cell[1]
			max_y = selected_cell[1]
def move_selected_cell(direction):
	global selected_cell, needs_redraw
	if selected_cell != None:
		if direction == "up": selected_cell = (selected_cell[0], max(selected_cell[1] - 1, 0))
		elif direction == "down": selected_cell = (selected_cell[0], min(selected_cell[1] + 1, rows - 1))
		elif direction == "left": selected_cell = (max(selected_cell[0] - 1, 0), selected_cell[1])
		elif direction == "right": selected_cell = (min(selected_cell[0] + 1, cols - 1), selected_cell[1])
		needs_redraw = True

def resize_selected_grid(direction):
	global selected_cell, needs_redraw, min_x, max_x, min_y, max_y
	
	if direction == "up": 
		for i in range(min_x, max_x + 1):
			if min_y - 1 >= 0:
				selected_grid.append((i, min_y - 1))
	elif direction == "down": 
		for i in range(min_x, max_x + 1):
			if max_y + 1 <= rows - 1:
				selected_grid.append((i, max_y + 1))
	elif direction == "left":
		for i in range(min_y, max_y + 1):
			if min_x - 1 >= 0:
				selected_grid.append((min_x - 1, i))
	elif direction == "right":
		for i in range(min_y, max_y + 1):
			if max_x + 1 <= cols - 1:
				selected_grid.append((max_x + 1, i))

	calculate_selection_limits()

	needs_redraw = True

def move_selected_grid(direction):
	global selected_cell, needs_redraw, min_x, max_x, min_y, max_y
	if direction == "up": 
		if selected_grid != []: resize_selected_grid("up")
		for i in range(min_x, max_x + 1):
			if (i, max_y) in selected_grid:	
				selected_grid.remove((i, max_y))

	elif direction == "down": 
		if selected_grid != []: resize_selected_grid("down")
		for i in range(min_x, max_x + 1):
			if (i, min_y) in selected_grid:	
				selected_grid.remove((i, min_y))

	elif direction == "left":
		if selected_grid != []: resize_selected_grid("left")
		for i in range(min_y, max_y + 1):
			if (max_x, i) in selected_grid:	
				selected_grid.remove((max_x, i))
		
	elif direction == "right":
		if selected_grid != []: resize_selected_grid("right")
		for i in range(min_y, max_y + 1):
			if (min_x, i) in selected_grid:	
				selected_grid.remove((min_x, i))

def move_selection(a0 : int, af : int, b0 : int, bf : int, direction, move : bool = True):
	global min_x, max_x, min_y, max_y
	step = 1 if direction in ("up", "left") else -1
	vertical = direction in ("up", "down")
	for i in range(a0, af):
		for cell in range(b0, bf, step):
			if vertical:
				grid[i][cell] = grid[i][cell + step]
			else:
				grid[cell][i] = grid[cell + step][i]
		if vertical:
			grid[i][bf] = " "
		else:
			grid[bf][i] = " "

	calculate_selection_limits()
	
	if move:
		move_selected_grid(direction)
		move_selected_cell(direction)
	grid_changed()

def set_cell_value(x: int, y: int, character: str, grid : list[list[str]] = grid) -> None:
	if 0 <= x < cols and 0 <= y < rows:
		grid[x][y] = character
		
def set_selected_cells_value(character):
	global selected_grid, selected_cell, needs_redraw, free_selection
	if selected_grid != []:
		for x, y in selected_grid:
			grid[x][y] = character
		selected_grid = []
	else:
		if selected_cell != None:
			grid[selected_cell[0]][selected_cell[1]] = character
			if character != " ":
				selected_cell = (min(selected_cell[0] + 1, cols - 1), selected_cell[1])
	if free_selection != []:
		for x, y in free_selection:
			grid[x][y] = character
		free_selection = []
	needs_redraw = True
	grid_changed()

def draw_grid_border():
	if not show_grid:
		return
	for x in range(cols):
		for y in range(rows):
			rect_area = pygame.Rect(x * rect_x, y * rect_y, rect_x, rect_y)
			pygame.draw.rect(screen, (16, 16, 16), rect_area, 1)

def draw_ascii(condition, grid : list[list[str]], background : bool):
	if not condition:
		return
	for x in range(cols):
		for y in range(rows):
			cell = grid[x][y]
			if isinstance(cell, str) and cell != " " and cell != "":
				if background:
					pygame.draw.rect(screen, background_color, (x * rect_x, y * rect_y, rect_x, rect_y))
				screen.blit(get_text_surface(cell), (x * rect_x, y * rect_y))

def copy_selection():
	if selected_grid and len(selected_grid) > 0:
		min_y = min(cell[1] for cell in selected_grid)
		max_y = max(cell[1] for cell in selected_grid)
		min_x = min(cell[0] for cell in selected_grid)
		max_x = max(cell[0] for cell in selected_grid)
		lines : list[str] = []
		for y in range(min_y, max_y + 1):
			line : str = ""
			for x in range(min_x, max_x + 1):
				line += str(grid[x][y])
			lines.append(line)
		text : str = "\n".join(lines)
		root = tk.Tk()
		root.withdraw()
		root.clipboard_clear()
		root.clipboard_append(text)
		root.update()
		root.destroy()
	elif selected_cell != None and str(grid[selected_cell[0]][selected_cell[1]]) != "":
		root = tk.Tk()
		root.withdraw()
		root.clipboard_clear()
		root.clipboard_append(grid[selected_cell[0]][selected_cell[1]])
		root.update()
		root.destroy()

def paste():
	global needs_redraw
	root = tk.Tk()
	root.withdraw()
	root.update()
	try:
		text = root.clipboard_get()
	except:
		text = ""
	root.destroy()
	
	if text and selected_cell != None:
		text = text.replace("\t", "    ")
		lines = text.splitlines()
		while lines and lines[0].strip() == "":
			lines.pop(0)
		while lines and lines[-1].strip() == "":
			lines.pop(-1)
		if not lines:
			return
		min_indent: int = min((len(line) - len(line.lstrip(" "))) for line in lines if line.strip() != "")
		start_x: int = selected_cell[0]
		start_y: int = selected_cell[1]
		
		for dy, line in enumerate(lines):
			clean_line: str = line[min_indent:].rstrip(" ")
			started = False 
			for dx, char in enumerate(clean_line):
				if not started:
					if char == " " or char == "":
						continue
					else:
						started = True  
				y: int = start_y + dy
				x: int = start_x + dx
				if 0 <= y < rows and 0 <= x < cols:
					grid[x][y] = char
					
		needs_redraw = True
		grid_changed()

def flip_ascii(axis):
	global selected_grid
 
	temporal_grid = []
 
	if axis == "horizontally":
		for x in range(min_x, max_x + 1):
			temporal_line = []
			for y in range(min_y, max_y + 1):
				temporal_line.append(grid[x][y])
			temporal_grid.append(temporal_line)
		temporal_grid.reverse()
 
	elif axis == "vertically":
		for x in range(min_x, max_x + 1):
			temporal_line = []
			for y in range(min_y, max_y + 1):
				temporal_line.append(grid[x][y])
			temporal_line.reverse()
			temporal_grid.append(temporal_line)
 
	chars = []
	for line in temporal_grid:
		for char in line:
			chars.append(char)
 
	char_iter = iter(chars)
 
	for x, y in selected_grid:
		grid[x][y] = next(char_iter)

def mirror_chars(axis):
	flipped_chars : list[tuple[str, str]] = []
	if axis == "horizontally":
		flipped_chars = h_flipped_chars
	elif axis == "vertically":
		flipped_chars = v_flipped_chars
	for x, y in selected_grid:
		current_char = grid[x][y]
 
		for tup in flipped_chars:
			for char in tup:
				if current_char == char:
					if char == tup[0]:
						grid[x][y] = tup[1]
					else:
						grid[x][y] = tup[0]
					break
			else:
				continue
			break

def randomize():
	global selected_grid, needs_redraw
 
	if selected_grid != []:
		for x, y in selected_grid:
			if grid[x][y] in ("$", "#", "&", "@"):
				grid[x][y] = random.choice(["$", "#", "&", "@"])
		needs_redraw = True
		grid_changed()
	else:
		for x in range(cols):
			for y in range(rows):
				if grid[x][y] in ("$", "#", "&", "@"):
					grid[x][y] = random.choice(["$", "#", "&", "@"])
		needs_redraw = True
		grid_changed()

def change_theme():
	global night_theme, background_color, chars_color
	night_theme = -night_theme
	if night_theme == True:
		background_color = (0, 0, 0)
		chars_color = (255, 255, 255)
	else:
		background_color = (255, 255, 255)
		chars_color = (0, 0, 0)
	text_cache.clear()

def handle_zoom(i : int):
	global font, rect_x, rect_y, needs_redraw, current_zoom
	if 1 <= current_zoom + i <= 4:
		current_zoom += i
		font = pygame.font.Font(font_name, current_zoom * 16)
		rect_x = current_zoom * 8
		rect_y = current_zoom * 16
		text_cache.clear()
		needs_redraw = True

# endregion Grid
# region Highlights

def handle_highlight_timer():												# Maneja Contador Destaque Celda
	global highlight_timer, highlight_state, needs_redraw
	if highlight_timer != None:
		current_time = pygame.time.get_ticks()
		if current_time - highlight_timer >= 500:
			highlight_state = 1 - highlight_state
			highlight_timer = current_time
			needs_redraw = True

def highlight_selected_cell():												# Destaca Celda Seleccionada
	if selected_cell != None:
		rect_area = pygame.Rect(selected_cell[0] * rect_x, selected_cell[1] * rect_y, rect_x, rect_y)
		rect_border = pygame.Rect(selected_cell[0] * rect_x, selected_cell[1] * rect_y, rect_x, rect_y)
		if highlight_state == 1 and screen.get_rect().contains(rect_area):
			sub_surface : pygame.Surface = screen.subsurface(rect_area).copy()
			inverted : pygame.Surface = pygame.Surface((rect_x, rect_y))
			for py in range(rect_y):
				for px in range(rect_x):
					color : tuple[int, int, int] = sub_surface.get_at((px, py))
					inv_color : tuple[int, int, int] = (255 - color.r, 255 - color.g, 255 - color.b)
					inverted.set_at((px, py), inv_color)
			screen.blit(inverted, rect_area.topleft)
		pygame.draw.rect(screen, (255, 255, 255), rect_border, 1)

def highlight_selected_grid(surface: pygame.Surface):
	selection = selected_grid + free_selection
	if selection != []:
		selected_set = set(selection)
		for x, y in selection:
			cell_rect = pygame.Rect(x * rect_x, y * rect_y, rect_x, rect_y)
			if (x, y - 1) not in selected_set:
				pygame.draw.line(surface, chars_color, 
					(cell_rect.left, cell_rect.top), 
					(cell_rect.right, cell_rect.top), 1)
			if (x, y + 1) not in selected_set:
				pygame.draw.line(surface, chars_color, 
					(cell_rect.left, cell_rect.bottom), 
					(cell_rect.right, cell_rect.bottom), 1)
			if (x - 1, y) not in selected_set:
				pygame.draw.line(surface, chars_color, 
					(cell_rect.left, cell_rect.top), 
					(cell_rect.left, cell_rect.bottom), 1)
			if (x + 1, y) not in selected_set:
				pygame.draw.line(surface, chars_color, 
					(cell_rect.right, cell_rect.top), 
					(cell_rect.right, cell_rect.bottom), 1)
# endregion Highlights
# region Algebra

def obj_to_matrix(file_path: str) -> tuple[list[list[float]], list[list[int]]]:
	vertices: list[list[float]] = []
	faces: list[list[int]] = []
	with open(file_path, "r", encoding="utf-8") as file:
		for line in file:
			line = line.strip()
			if not line or line.startswith("#"):
				continue
			parts = line.split()
			prefix = parts[0]

			if prefix == "v":
				x, y, z = map(float, parts[1:4])
				vertices.append([x, y, z])
			elif prefix == "f":
				face_indices = []
				for part in parts[1:]:
					vertex_idx = int(part.split("/")[0]) - 1
					face_indices.append(vertex_idx)
				faces.append(face_indices)
	return vertices, faces

def fix_winding(vertices: list[list[float]], faces: list[list[int]]) -> list[list[int]]:
	edge_faces: dict[tuple[int, int], list[int]] = {}
	for i, f in enumerate(faces):
		for j in range(len(f)):
			a, b = f[j], f[(j + 1) % len(f)]
			key = (min(a, b), max(a, b))
			edge_faces.setdefault(key, []).append(i)
	visited = [False] * len(faces)
	oriented = [f[:] for f in faces]
	for start in range(len(faces)):
		if visited[start]:
			continue
		visited[start] = True
		component = [start]
		stack = [start]
		while stack:
			current = stack.pop()
			f = oriented[current]
			for j in range(len(f)):
				a, b = f[j], f[(j + 1) % len(f)]
				key = (min(a, b), max(a, b))
				for other_i in edge_faces[key]:
					if other_i == current or visited[other_i]:
						continue
					other_f = oriented[other_i]
					idx = other_f.index(a)
					if other_f[(idx + 1) % len(other_f)] == b:
						oriented[other_i] = other_f[::-1]
					visited[other_i] = True
					stack.append(other_i)
					component.append(other_i)
		volume = 0
		for i in component:
			f = oriented[i]
			for k in range(1, len(f) - 1):
				p0, p1, p2 = vertices[f[0]], vertices[f[k]], vertices[f[k + 1]]
				volume += (p0[0]*(p1[1]*p2[2]-p1[2]*p2[1]) - p0[1]*(p1[0]*p2[2]-p1[2]*p2[0]) + p0[2]*(p1[0]*p2[1]-p1[1]*p2[0]))
		if volume < 0:
			for i in component:
				oriented[i] = oriented[i][::-1]
	return oriented

def draw_line(p1: tuple[int, int], p2: tuple[int, int], char: str = "$", grid : list[list[str]] = grid):
	x1, y1 = map(int, p1)
	x2, y2 = map(int, p2)
	dx = x2 - x1
	dy = y2 - y1

	if dx == 0:
		y_start, y_end = sorted([y1, y2])
		for y in range(y_start, y_end + 1):
			set_cell_value(x1, y, char, grid)
		return

	elif dy == 0:
		x_start, x_end = sorted([x1, x2])
		for x in range(x_start, x_end + 1):
			set_cell_value(x, y1, char, grid)
		return

	else:
		m = dy / dx
		x_start, x_end = sorted([x1, x2])
		for x in range(x_start, x_end + 1):
			y = int(m * (x - x1) + y1)
			set_cell_value(x, y, char, grid)
		y_start, y_end = sorted([y1, y2])
		for y in range(y_start, y_end + 1):
			x = int(((y - y1) / m) + x1)
			set_cell_value(x, y, char, grid)
		return

def scalar_multiplication(scalar : float, vertices : list[list[float]]) -> list[list[float]]:
	for vertex in vertices:
		for i in range(len(vertex)):
			vertex[i] *= scalar
	return vertices

def axes_scalar_multiplication(axes : tuple[float, float, float], vertices : list[list[float]]) -> list[list[float]]:
	for i, scalar in enumerate(axes):
		for vertex in vertices:
			vertex[i] *= scalar
	return vertices

def axes_scalar_translation(axes : tuple[float, float, float], vertices : list[list[float]]) -> list[list[float]]:
	for i, scalar in enumerate(axes):
		for vertex in vertices:
			vertex[i] += scalar
	return vertices

def rotate_vertices( axes : tuple[float, float, float], vertices: list[list[float]]):
	angle_x, angle_y, angle_z = math.radians(axes[0]), math.radians(axes[1]), math.radians(axes[2])
	cx, sx = math.cos(angle_x), math.sin(angle_x)
	cy, sy = math.cos(angle_y), math.sin(angle_y)
	cz, sz = math.cos(angle_z), math.sin(angle_z)
	for vertex in vertices:
		x, y, z = vertex[0], vertex[1], vertex[2]
		if axes[0] != 0:
			y, z = y*cx - z*sx, y*sx + z*cx
		if axes[1] != 0:
			x, z = x*cy + z*sy, -x*sy + z*cy
		if axes[2] != 0:
			x, y = x*cz - y*sz, x*sz + y*cz
		vertex[0], vertex[1], vertex[2] = x, y, z
	return vertices

def R3_R2(vertices : list[list[float]]) -> list[list[float]]:
	for v in vertices:
		del v[2]
	return vertices

def IGAR_transformation(axes : tuple[float, float], vertices : list[list[float]]) -> list[list[float]]:
	for i, scalar in enumerate(axes):
		for vertex in vertices:
			vertex[i] *= scalar
	return vertices

def vertices_faces_to_vectors(vertices: list[list[float]], faces: list[list[int]], faces_pointing : list[float], solid_mode : bool) -> list[tuple[list[float], list[float]]]:
	vectors : list[tuple[list[float], list[float]]] = []
	for j, f in enumerate(faces):
		if faces_pointing[j] > 0 or not solid_mode:
			for i in range(len(f)):
				if i == len(f) - 1:
						vectors.append((vertices[f[i]], vertices[f[0]]))
				else:
						vectors.append((vertices[f[i]], vertices[f[i+1]]))
	return vectors

def get_faces_perimeter(faces: list[list[int]], vecs: list[tuple[list[float], list[float]]], faces_pointing: list[float]):
	offset = 0
	if faces_pointing[0] > 0:
		qty = 4
		for q in range(qty):
			print(vecs[offset + q])
		offset += qty
		# NO SEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE

def get_faces_normals(vertices: list[list[float]], faces: list[list[int]]) -> list[list[float]]:
	normals: list[list[float]] = []
	for f in faces:
		nx, ny, nz = 0, 0, 0
		for i in range(len(f)):
			p0 = vertices[f[i]]
			p1 = vertices[f[(i + 1) % len(f)]]
			nx += (p0[1] - p1[1]) * (p0[2] + p1[2])
			ny += (p0[2] - p1[2]) * (p0[0] + p1[0])
			nz += (p0[0] - p1[0]) * (p0[1] + p1[1])
		normals.append([nx, ny, nz])
	return normals

def compare_normals_to_camera(normals : list[list[float]]) -> list[float]:
	faces_pointing : list[float] = []
	for normal in normals:
		if normal[2] < 0:
			faces_pointing.append(1)
		else:
			faces_pointing.append(-1)
	return faces_pointing

def get_faces_centers(vertices: list[list[float]], faces: list[list[int]], faces_pointing : list[float], solid_mode : bool) -> list[list[float]]:
	x_coords : list[list[float]] = []
	y_coords : list[list[float]] = []
	for j, f in enumerate(faces):
		if faces_pointing[j] > 0 or not solid_mode:
			x_face: list[float] = []
			y_face: list[float] = []
			for vertex_index in f:
				x_face.append(vertices[vertex_index][0])
				y_face.append(vertices[vertex_index][1])
			x_coords.append(x_face)
			y_coords.append(y_face)
	for f in x_coords:
		f.sort()
	for f in y_coords:	
		f.sort()
	faces_centers : list[list[float]] = [[0, 0] for _ in x_coords]
	for i, c in enumerate(x_coords):
		faces_centers[i][0] = (c[len(c)-1] + c[0])/2
	for i, c in enumerate(y_coords):
		faces_centers[i][1] = (c[len(c)-1] + c[0])/2
	return faces_centers

def render_object(obj_file_path: str, multiplication_axes : tuple[float, float, float], translation_axes : tuple[float, float, float], rotation_axes : tuple[float, float, float], solid_mode : bool = False):
	global needs_redraw, obj_cache, obj_free_selection
	vertices : list[list[float]] = []
	faces : list[list[int]] = [] 
	if obj_file_path not in obj_cache:
		base_vertices, base_faces = obj_to_matrix(obj_file_path)
		obj_cache[obj_file_path] = (base_vertices, fix_winding(base_vertices, base_faces))
		
	base_vertices, base_faces = obj_cache[obj_file_path]
	vertices = [v[:] for v in base_vertices]
	faces = base_faces
	
	rotate_vertices(rotation_axes, vertices)
	axes_scalar_multiplication(multiplication_axes, vertices)
	axes_scalar_translation(translation_axes, vertices)
	normals = get_faces_normals(vertices, faces)
	faces_pointing = compare_normals_to_camera(normals)
	R3_R2(vertices)
	IGAR_transformation([2,-1], vertices)

	vecs : list[tuple[list[float], list[float]]] = []
	vecs = vertices_faces_to_vectors(vertices, faces, faces_pointing, solid_mode)

	for v in vecs:
		draw_line(v[0], v[1], "$", obj_grid)
	needs_redraw = True
	if solid_mode:
		faces_centers : list[list[float]] = []
		faces_centers = get_faces_centers(vertices, faces, faces_pointing, solid_mode)
		for c in faces_centers:
			face_fill : list[tuple[int, int]] = []
			if 0 <= int(c[1]) < rows and 0 <= int(c[0]) < cols:
				if obj_grid[int(c[0])][int(c[1])] != "$":
					magic_wand(int(c[0]), int(c[1]), obj_grid, face_fill)
					leaked : bool = False
					for x, y in face_fill:
						if x == 0 or x == cols - 1 or y == 0 or y == rows - 1:
							leaked = True
							break
					if not leaked:
						obj_free_selection.extend(face_fill)
		if obj_free_selection != []:
			for x, y in obj_free_selection:
				obj_grid[x][y] = "○"
			obj_free_selection = []

def sin_func(variable : int, amplitude : int = 360, period : int = 720):
	sin = amplitude * math.sin((2 * math.pi / period) * variable)
	return sin

# endregion Algebra
# region Matrix Rain

def matrix():
	global matrix_mode, matrix_start_time, matrix_delay
	matrix_mode = not matrix_mode
	matrix_start_time = pygame.time.get_ticks()
	matrix_delay = 0

class matrix_drop:
	def __init__(self, x_pos, velocity):
		self.drop_start_time = pygame.time.get_ticks()
		self.drop_delay = 0
		self.current_y_pos = 0
		self.x_pos = x_pos
		self.velocity = velocity
		self.dead = False
		self.collisioned : bool = False
		self.gradient_1 = random.choice(["Ñ", "$", "#", "&", "@"])
		self.collisioned_y_pos : int = -1
		self.trail_length = random.randint(33, 42)
		self.quarter = self.trail_length // 4
 
	def update(self):
		current_time = pygame.time.get_ticks()
		if (current_time - self.drop_delay) - self.drop_start_time > 0:
			self.current_y_pos += 1
			self.drop_delay += self.velocity
 
			self.gradient_1 = random.choice(["Ñ", "$", "#", "&", "@"])
			self.gradient_2 = [random.choice(["I", "|", "i"]) for _ in range(self.quarter)]
			self.gradient_3 = [random.choice([":", ";"]) for _ in range(self.quarter)]
			self.gradient_4 = ["∙" for _ in range(self.quarter)]
			self.gradient_5 = ["·" for _ in range(self.quarter)]
			self.gradient_list = [self.gradient_2, self.gradient_3, self.gradient_4, self.gradient_5]
 
		if self.current_y_pos < rows:
			set_cell_value(self.x_pos, self.current_y_pos, self.gradient_1, matrix_grid)
		for current_qrtr in range(1, 5):
			quarter_y_pos = self.current_y_pos - current_qrtr * self.quarter
			for i in range(quarter_y_pos, self.current_y_pos - (current_qrtr - 1) * self.quarter):
				if 0 <= i < rows:
					set_cell_value(self.x_pos, i, self.gradient_list[current_qrtr - 1][i - (quarter_y_pos)], matrix_grid)
		if self.current_y_pos - self.trail_length >= rows:
			self.dead = True
		if drop_collision:
			if self.current_y_pos < rows:
				if grid[self.x_pos][self.current_y_pos] != " " and self.collisioned_y_pos == -1:
					self.collisioned = True
					self.collisioned_y_pos = self.current_y_pos
			if self.collisioned == True:
				if self.collisioned_y_pos > 0:
					set_cell_value(self.x_pos - 1 , self.collisioned_y_pos - 1, "\\", matrix_grid)
					set_cell_value(self.x_pos + 1 , self.collisioned_y_pos - 1, "/", matrix_grid)
					set_cell_value(self.x_pos, self.collisioned_y_pos - 1, "↓", matrix_grid)
				for o in range(self.collisioned_y_pos, rows):
					set_cell_value(self.x_pos, o - 1, "↓", matrix_grid)
				if self.current_y_pos - self.trail_length >= self.collisioned_y_pos:
					self.dead = True

# endregion Matrix Rain
# region DVD

def handle_dvd():
	global dvd_mode, dvd_start_time, dvd_delay
	dvd_mode = not dvd_mode
	dvd_start_time = pygame.time.get_ticks()
	dvd_delay = 0

class dvd:
	def __init__(self, x_pos, y_pos):
		self.x_pos = x_pos
		self.y_pos = y_pos
		self.x_velocity : int = 2
		self.y_velocity : int = 1
	def update(self):
		for dx in range(40):
			for dy in range(9):
				set_cell_value(self.x_pos + dx, self.y_pos + dy, " ", dvd_grid)
		if self.x_pos + self.x_velocity + 40 >= cols or self.x_pos + self.x_velocity < 0:
			self.x_velocity *= -1
		if self.y_pos + self.y_velocity + 8 >= rows or self.y_pos + self.y_velocity < 0:
			self.y_velocity *= -1
		self.x_pos += self.x_velocity
		self.y_pos += self.y_velocity
		for dy, line in enumerate(dvd_art):
			for dx, char in enumerate(line):
				if char != " ":
					set_cell_value(self.x_pos + dx, self.y_pos + dy, char, dvd_grid)

# endregion DVD
# endregion funcs

# region Initialization
clock = pygame.time.Clock()
grids.append(copy.deepcopy(grid))
running = True
draw_layers = [
	(0, lambda: screen.fill(background_color)),
	(1, draw_grid_border),
	(2, lambda: draw_ascii(matrix_drops, matrix_grid, False)),
	(3, lambda: draw_ascii(needs_redraw, grid, True)),
	(3, lambda: draw_ascii(obj_mode, obj_grid, True)),
	(4, handle_ui),
	(4, lambda: draw_ascii(visible_ui, ui_grid, True)),
	(6, highlight_selected_cell),
	(5, draw_igar_keyboard_shortcuts),
	(6, lambda: draw_ascii(dvd_mode, dvd_grid, True))
]

# endregion Initialization
while running:
# region Conditionless

	handle_highlight_timer()
	
	if selected_grid != []:
		min_y = min(cell[1] for cell in selected_grid)
		max_y = max(cell[1] for cell in selected_grid)
		min_x = min(cell[0] for cell in selected_grid)
		max_x = max(cell[0] for cell in selected_grid)
	else: 
		if selected_cell != None:
			min_y = selected_cell[1]
			max_y = selected_cell[1]
			min_x = selected_cell[0]
			max_x = selected_cell[0]

	if obj_mode:
		current_time = pygame.time.get_ticks()

		if current_time - obj_last_render >= 10:
			obj_last_render = current_time
			obj_degree += 1
			visible_cols = screen.get_width() // rect_x
			visible_rows = screen.get_height() // rect_y
			for x in range(cols):
				for y in range(rows):
					obj_grid[x][y] = " "
			render_object("IGAR_data\cube.obj", [15, 15, 15], [visible_cols/4, -visible_rows/2, 0], [sin_func(obj_degree), sin_func(obj_degree, 360, 1080), sin_func(obj_degree, 360, 1440)], True)
			# render_object("IGAR_data\cube.obj", [25, 25, 25], [60, -32, 0], [sin_func(obj_degree, 360, 1080), sin_func(obj_degree, 360, 1440), sin_func(obj_degree)], False)
			
# endregion Conditionless
# region Events

	for event in pygame.event.get():
# region Quit IGAR
		if event.type == pygame.QUIT:
			close_igar(event)
		elif event.type == pygame.WINDOWMINIMIZED:
			window_visible = False
		elif event.type == pygame.WINDOWRESTORED or event.type == pygame.WINDOWEXPOSED:
			window_visible = True
		elif event.type == pygame.WINDOWFOCUSLOST:
			window_focused = False
		elif event.type == pygame.WINDOWFOCUSGAINED:
			window_focused = True
# endregion Quit IGAR
# region Mouse Events

		elif event.type == pygame.MOUSEMOTION:												# Mouse Motion
			mouse_x, mouse_y = event.pos
			clicked_col : int = min(mouse_x // rect_x, cols - 1)
			clicked_row : int = min(mouse_y // rect_y, rows - 1)
			grided_pos : list[str] = (clicked_col, clicked_row)
			if pygame.mouse.get_pressed()[0]:  
				
				if drawing_mode:
					if pygame.mouse.get_pressed()[0]:
						set_cell_value(clicked_col, clicked_row, "$", grid)
						draw_line(past_mouse_pos, grided_pos)
						needs_redraw = True
					elif pygame.mouse.get_pressed()[2]:
						draw_line(past_mouse_pos, grided_pos, " ")
						needs_redraw = True
				else:
					highlight_state = 1
					highlight_timer = pygame.time.get_ticks()
					mouse_x, mouse_y = event.pos
					last_selected_cell = (clicked_col, clicked_row)
					if first_selected_cell != None and last_selected_cell != None:
						selected_grid = []
						for x in range(min(first_selected_cell[0], last_selected_cell[0]), max(first_selected_cell[0], last_selected_cell[0]) + 1):
							for y in range(min(first_selected_cell[1], last_selected_cell[1]), max(first_selected_cell[1], last_selected_cell[1]) + 1):
								selected_grid.append((x, y))
						selected_cell = last_selected_cell
					needs_redraw = True
			past_mouse_pos = grided_pos
		elif event.type == pygame.MOUSEBUTTONDOWN:											# Mouse Click
			if event.button == 1:															# Left Click
				highlight_timer = pygame.time.get_ticks()
				highlight_state = 1						
				first_selected_cell = (clicked_col, clicked_row)
				if drawing_mode:
					past_mouse_pos = (clicked_col, clicked_row)
					set_cell_value(clicked_col, clicked_row, "$", grid)
				if selected_grid != []:
					selected_grid = []
				needs_redraw = True
			elif event.button == 2:															# Testing Testing
				print("min_x", min_x , "max_x", max_x , "min_y", min_y ,"max_y", max_y)
			elif event.button == 3:															# Right Click
				selected_cell = None
				selected_grid = []
				needs_redraw = True
			elif event.button == 4:															# Scroll Up
				handle_zoom(1)
			elif event.button == 5:															# Scroll Down
				handle_zoom(-1)
		elif event.type == pygame.MOUSEBUTTONUP:											# Mouse Up
			if drawing_mode:
				grid_changed()
			elif event.button == 1:															# Left Click
				last_selected_cell = (clicked_col, clicked_row)
				if first_selected_cell != None and last_selected_cell != None:
					selected_cell = (clicked_col, clicked_row)
					if first_selected_cell == last_selected_cell:
						selected_grid = []
					else:
						selected_grid = []
						for x in range(min(first_selected_cell[0], last_selected_cell[0]), max(first_selected_cell[0], last_selected_cell[0]) + 1):
							for y in range(min(first_selected_cell[1], last_selected_cell[1]), max(first_selected_cell[1], last_selected_cell[1]) + 1):
								selected_grid.append((x, y))
				needs_redraw = True

# endregion Mouse Events
# region Keyboard Events

		elif event.type == pygame.KEYDOWN:
			highlight_timer = pygame.time.get_ticks()
			highlight_state = 1
			needs_redraw = True

# region Alt - Shortcuts

			if event.mod & pygame.KMOD_RALT:
				if event.key == pygame.K_n:
					set_selected_cells_value('♪')

# endregion Alt - Shortcuts
# region Ctrl + Shift - Shortcuts

			if event.mod & pygame.KMOD_CTRL and event.mod & pygame.KMOD_SHIFT and not event.mod & pygame.KMOD_RALT:
				if event.key == pygame.K_h:													# Ctrl + Shift + H
					flip_ascii("horizontally")
					mirror_chars("horizontally")
					needs_redraw = True
					grid_changed()
				elif event.key == pygame.K_v:												# Ctrl + Shift + V
					flip_ascii("vertically")
					mirror_chars("vertically")
					needs_redraw = True
					grid_changed()
				elif event.key == pygame.K_w:												# Ctrl + Shift + W
					if selected_cell != None:
						absolute_magic_wand(selected_cell[0], selected_cell[1], grid, free_selection)
				elif event.key == pygame.K_s:												# Ctrl + Shift + S
					save_grid_as()
				elif event.key == pygame.K_e:												# Ctrl + Shift + E
					export_path = export_canvas(screen)
					last_export_path = export_path
				elif event.key == pygame.K_t:												# Ctrl + Shift + T
					change_theme()
				elif event.key == pygame.K_m:												# Ctrl + Shift + M
					matrix()
					drop_collision = True
				elif event.key == pygame.K_o:												# Ctrl + Shift + O
					obj_mode = not obj_mode
				elif event.key == pygame.K_d:												# Ctrl + Shift + D
					handle_dvd()

# endregion Ctrl + Shift - Shortcuts
# region Ctrl - Shortcuts

# region Editor Commands
			elif event.mod & pygame.KMOD_CTRL and not event.mod & pygame.KMOD_RALT:
				if event.key == pygame.K_g:													# Ctrl + G
					show_grid = not show_grid
				elif event.key == pygame.K_w:												# Ctrl + W
					if selected_cell != None:
						magic_wand(selected_cell[0], selected_cell[1], grid, free_selection)
				elif event.key == pygame.K_t:												# Ctrl + T
					toggle_topmost()
				elif event.key == pygame.K_n:												# Ctrl + N
					new_grid()
				elif event.key == pygame.K_s:												# Ctrl + S
					save_grid()
				elif event.key == pygame.K_o:												# Ctrl + O
					load_grid()
				elif event.key == pygame.K_e:												# Ctrl + E
					if last_export_path and os.path.exists(last_export_path):
						save_canvas_as_png(screen, last_export_path)
					else:
						export_path = export_canvas(screen)
						last_export_path = export_path
				elif event.key == pygame.K_z:												# Ctrl + Z
					undo()
				elif event.key == pygame.K_y:												# Ctrl + Y
					redo()
				elif event.key == pygame.K_f:												# Ctrl + F
					visible_ui = not visible_ui
				elif event.key == pygame.K_r:												# Ctrl + R
					randomize()
				elif event.key == pygame.K_c:												# Ctrl + C
					copy_selection()
				elif event.key == pygame.K_x:												# Ctrl + X
					copy_selection()
					set_selected_cells_value(" ")
				elif event.key == pygame.K_v:												# Ctrl + V
					paste()
				elif event.key == pygame.K_m:												# Ctrl + M
					matrix()
					drop_collision = False
				elif event.key == pygame.K_d:												# Ctrl + D
					drawing_mode = not drawing_mode

# endregion Editor Commands
# region Special Chars
				elif event.key == 124:														# Ctrl + |
					set_selected_cells_value("₊")
				elif event.key == pygame.K_1:												# Ctrl + 1
					set_selected_cells_value("…")
				elif event.key == pygame.K_2:												# Ctrl + 2
					set_selected_cells_value("·")
				elif event.key == pygame.K_3:												# Ctrl + 3
					set_selected_cells_value("•")
				elif event.key == pygame.K_4:												# Ctrl + 4
					set_selected_cells_value('○')
				elif event.key == pygame.K_5:												# Ctrl + 5
					set_selected_cells_value('·')
				elif event.key == pygame.K_6:												# Ctrl + 6
					set_selected_cells_value('״')
				elif event.key == pygame.K_7:												# Ctrl + 7
					set_selected_cells_value('ª')
				elif event.key == pygame.K_8:												# Ctrl + 8
					set_selected_cells_value('˙')
				elif event.key == pygame.K_9:												# Ctrl + 9
					set_selected_cells_value("░")
				elif event.key == pygame.K_0:												# Ctrl + 0
					set_selected_cells_value("▒")
				elif event.key == pygame.K_QUOTE:											# Ctrl + '
					set_selected_cells_value("▓")
				elif event.key == 191:														# Ctrl + ¿
					set_selected_cells_value("█")

# endregion Special Chars
# region Jump Selected Cell

				elif event.key == pygame.K_HOME:											# Ctrl + Home
					for x in range(0, selected_cell[0]):
						if grid[x][selected_cell[1]] != " ":
							selected_cell = (x, selected_cell[1])
							break
						selected_cell = (0, selected_cell[1])
				elif event.key == pygame.K_END:												# Ctrl + End
					for x in range(cols - 1, selected_cell[0] - 1, -1):
						if grid[x][selected_cell[1]] != " ":
							selected_cell = (x + 1, selected_cell[1])
							break
						selected_cell = (cols - 1, selected_cell[1])
				elif event.key == pygame.K_PAGEUP:											# Ctrl + Page Up
					for y in range(0, selected_cell[1]):
						if grid[selected_cell[0]][y] != " ":
							selected_cell = (selected_cell[0], y)
							break
						selected_cell = (selected_cell[0], 0)
				elif event.key == pygame.K_PAGEDOWN:										# Ctrl + Page Down
					for y in range(rows - 1, selected_cell[1], -1):
						if grid[selected_cell[0]][y] != " ":
							selected_cell = (selected_cell[0], y)
							break
						selected_cell = (selected_cell[0], rows - 1)

# endregion Jump Selected Cell
# region Move Selected Grid

				if selected_cell != None:							# Ctrl + Arrows (Grid)
					if event.key == pygame.K_UP:											# Ctrl + Up
						if min_y == max_y or min_x == max_x:
							move_selection(min_x, max_x + 1, 0, rows - 1, "up", False)
						else:
							move_selection(min_x, max_x + 1, min_y - 1, max_y, "up")

					elif event.key == pygame.K_DOWN:										# Ctrl + Down
						if min_y == max_y or min_x == max_x:
							move_selection(min_x, max_x + 1, rows - 1, 0, "down", False)
						else:
							move_selection(min_x, max_x + 1, max_y + 1, min_y, "down")
	
					elif event.key == pygame.K_LEFT:										# Ctrl + Left
						if min_x == max_x or min_y == max_y:
							move_selection(min_y, max_y + 1, 0, cols - 1, "left", False)
						else:
							move_selection(min_y, max_y + 1, min_x - 1, max_x, "left")

					elif event.key == pygame.K_RIGHT:										# Ctrl + Right
						if min_x == max_x or min_y == max_y:
							move_selection(min_y, max_y + 1, cols - 1, 0, "right", False)
						else:
							move_selection(min_y, max_y + 1, max_x + 1, min_x, "right")


# endregion Move Selected Grid
# endregion Ctrl - Shortcuts
# region Shift - Shortcuts

			if selected_cell != None and event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT] and event.mod & pygame.KMOD_SHIFT:
				if first_selected_cell == None:
					first_selected_cell = selected_cell
				if event.key == pygame.K_UP:												# Shift + Up
					resize_selected_grid("up")
					move_selected_cell("up")
				elif event.key == pygame.K_DOWN:											# Shift + Down
					resize_selected_grid("down")
					move_selected_cell("down")
				elif event.key == pygame.K_LEFT:											# Shift + Left
					resize_selected_grid("left")
					move_selected_cell("left")					
				elif event.key == pygame.K_RIGHT:											# Shift + Right
					resize_selected_grid("right")
					move_selected_cell("right")
				continue

# endregion Shift - Shortcuts

			if event.mod & pygame.KMOD_CTRL and not event.mod & pygame.KMOD_RALT:
				continue
			
# region Chars

			else:
				if event.key == pygame.K_F8:												# F8/Escape
					close_igar(event)
				elif event.key == pygame.K_ESCAPE:
					if confirm_new_grid:
						confirm_new_grid = False
					elif confirm_exit: 	
						confirm_exit = False
					elif selected_cell == None and selected_grid == []:
						close_igar(event)
					else:
						if selected_grid != []:
							selected_grid = []
						elif free_selection != []:
							free_selection = []
						elif selected_cell != None:
							selected_cell = None
				elif event.key == pygame.K_F1:												# F1
					igar_keyboard_shortcuts = not igar_keyboard_shortcuts
				elif event.key == pygame.K_F11:												# F11
					if is_fullscreen:
						screen = pygame.display.set_mode(windowed_size, pygame.RESIZABLE)
						move_window(windowed_pos[0], windowed_pos[1])
						is_fullscreen = False
					else:
						restore_if_maximized()
						x, y, w, h = get_window_geometry()
						windowed_pos = (x, y)
						windowed_size = (w, h)
						monitor_rect = get_monitor_rect()
						screen = pygame.display.set_mode((monitor_rect.right - monitor_rect.left, monitor_rect.bottom - monitor_rect.top), pygame.NOFRAME)
						move_window(monitor_rect.left, monitor_rect.top)
						is_fullscreen = True

				if selected_cell != None:
					if event.key == pygame.K_BACKSPACE:										# Backspace
						move_selected_cell("left")
						set_selected_cells_value(" ")
						for cell in range(selected_cell[0], cols - 1):
							grid[cell][selected_cell[1]] = grid[cell + 1][selected_cell[1]]
					elif event.key == pygame.K_HOME:										# Home
						if grid[selected_cell[0]][selected_cell[1]] == " ":
							for x in range(selected_cell[0], 0, -1):
								if grid[x][selected_cell[1]] != " ":
									selected_cell = (x, selected_cell[1])
									break
							else:
								selected_cell = (0, selected_cell[1])
						else:
							for x in range(selected_cell[0], 0, -1):
								if grid[x][selected_cell[1]] == " ":
									selected_cell = (x, selected_cell[1])
									break
							else:
								selected_cell = (0, selected_cell[1])
					elif event.key == pygame.K_END:											# End
						if grid[selected_cell[0]][selected_cell[1]] == " ":
							for x in range(selected_cell[0], cols):
								if grid[x][selected_cell[1]] != " ":
									selected_cell = (x, selected_cell[1])
									break
							else:
								selected_cell = (cols - 1, selected_cell[1])
						else:
							for x in range(selected_cell[0], cols):
								if grid[x][selected_cell[1]] == " ":
									selected_cell = (x, selected_cell[1])
									break
							else:
								selected_cell = (cols - 1, selected_cell[1])
					elif event.key == pygame.K_PAGEUP:										# Page Up
						if grid[selected_cell[0]][selected_cell[1]] == " ":
							for y in range(selected_cell[1], 0, -1):
								if grid[selected_cell[0]][y] != " ":
									selected_cell = (selected_cell[0], y)
									break
							else:
								selected_cell = (selected_cell[0], 0)
						else:
							for y in range(selected_cell[1], 0, -1):
								if grid[selected_cell[0]][y] == " ":
									selected_cell = (selected_cell[0], y)
									break
							else:
								selected_cell = (selected_cell[0], 0)
					elif event.key == pygame.K_PAGEDOWN:									# Page Down
						if grid[selected_cell[0]][selected_cell[1]] == " ":
							for y in range(selected_cell[1], rows):
								if grid[selected_cell[0]][y] != " ":
									selected_cell = (selected_cell[0], y)
									break
							else:
								selected_cell = (selected_cell[0], rows - 1)
						else:
							for y in range(selected_cell[1], rows):
								if grid[selected_cell[0]][y] == " ":
									selected_cell = (selected_cell[0], y)
									break
							else:
								selected_cell = (selected_cell[0], rows - 1)
					elif event.key == pygame.K_ESCAPE:										# Escape
						matrix_mode = False
						selected_grid = []
					elif event.key == pygame.K_RETURN:										# Return
						move_selected_cell("down")
					elif event.key == pygame.K_TAB:											# Tab
						selected_cell = (min(selected_cell[0] + 4, cols - 1), selected_cell[1])
					elif event.key == pygame.K_DELETE:										# Delete
						set_selected_cells_value(" ")
						for cell in range(selected_cell[0], cols - 1):
							grid[cell][selected_cell[1]] = grid[cell + 1][selected_cell[1]]
					elif event.key == pygame.K_SPACE:										# Space
						set_selected_cells_value(" ")
						move_selected_cell("right")
					elif event.key == pygame.K_UP: move_selected_cell("up")					# Up
					elif event.key == pygame.K_DOWN: move_selected_cell("down")				# Down
					elif event.key == pygame.K_LEFT: move_selected_cell("left")				# Left
					elif event.key == pygame.K_RIGHT: move_selected_cell("right")			# Right
					else:
						char : str = event.unicode
						if char != "":
							set_selected_cells_value(char)

# endregion Chars
# endregion Keyboard Events
# endregion Events

# region Matrix Rain

	if matrix_mode:
		current_time = pygame.time.get_ticks()

		if (current_time - matrix_delay) - matrix_start_time > 0:
			x_pos = random.randint(0, cols - 1)
			if grid[x_pos][0] == " ":
				matrix_drops.append(matrix_drop(x_pos, random.randint(25, 200)))
			matrix_delay += random.randint(50, 100)
	if matrix_drops:
		for x in range(cols):
			for y in range(rows):
				matrix_grid[x][y] = " "
		for drop in matrix_drops[:]:
			drop.update()
			needs_redraw = True
			if drop.dead:
				matrix_drops.remove(drop)

# endregion Matrix Rain
# region DVD Screensaver
	if dvd_mode:
		if not dvd_exists:
			dvd_instance = dvd(0, 0)
			dvd_exists = not dvd_exists

		current_time = pygame.time.get_ticks()
		if (current_time - dvd_delay) - dvd_start_time > 0:
			dvd_delay += 48
			dvd_instance.update()
			needs_redraw = True

# endregion DVD Screensaver

	current_time = pygame.time.get_ticks()
	if current_time - visibility_check_timer >= visibility_check_interval:
		visibility_check_timer = current_time
		window_covered = is_desktop_fully_covered()

# region Drawing

	if needs_redraw and window_visible and not window_covered:
		hora = datetime.now()

		draw_layers.sort(key=lambda elemento: elemento[0])
		for func in draw_layers:
			func[1]()
			
		if selected_grid or free_selection:
			overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
			highlight_selected_grid(overlay)
			screen.blit(overlay, (0, 0))

		if confirm_new_grid:
			draw_popup_message("Are you sure you want to open a new grid without saving? (ESC to cancel, repeat to accept)")
		if confirm_exit:
			draw_popup_message("Are you sure you want to exit IGAR without saving? (ESC to cancel, repeat to accept)")
			
		pygame.display.update()
		needs_redraw = False

# endregion Drawing
	clock.tick(60)
	
pygame.quit()