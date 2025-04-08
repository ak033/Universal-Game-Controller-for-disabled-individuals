import tkinter as tk
from tkinter import ttk
import subprocess
import sys

class MotionCaptureApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Motion Capture App")
        self.geometry("1000x500")
        
        # Container to hold all frames
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Dictionary to store frames
        self.frames = {}
        
        # State to track which motion is being captured
        self.current_motion = None
        
        # State to track completed motions
        self.completed_motions = set()
        
        # Create and store all frames
        for F in (WelcomeFrame, MuscleSetupFrame, RequestMotionFrame, ErrorMotionFrame, 
                  CaptureMotionFrame, SuccessMotionFrame):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Show the initial frame
        self.show_frame("WelcomeFrame")
    
    def show_frame(self, frame_name):
        """Raise the specified frame to the top"""
        frame = self.frames[frame_name]
        
        # Update the frame if needed before displaying
        if hasattr(frame, "on_show"):
            frame.on_show()
            
        frame.tkraise()
    
    def start_motion_capture(self, motion_type):
        """Start the motion capture for a specific motion type"""
        self.current_motion = motion_type
        self.show_frame("RequestMotionFrame")
    
    def complete_motion_capture(self):
        """Mark the current motion as completed"""
        if self.current_motion:
            self.completed_motions.add(self.current_motion)
            self.current_motion = None

    def start_game(self):
        """Launch the game UI"""
        try:
            subprocess.Popen([sys.executable, "Universal-Game-Controller-for-Disabled-Individuals/UGCFDI Project/UI/gameUI.py"])
            self.quit()
        except Exception as e:
            tk.messagebox.showerror("Error", f"Could not start game: {str(e)}")

class WelcomeFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        
        label = ttk.Label(self, text="Hello, let's set up your muscles", font=("Helvetica", 24))
        label.pack(pady=20)
        
        button = tk.Button(
            self, 
            text="Start", 
            command=lambda: controller.show_frame("MuscleSetupFrame"), 
            width=40, 
            height=6
        )
        button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

class MuscleSetupFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        label = ttk.Label(self, text="Hello, let's set up your muscles", font=("Helvetica", 24))
        label.pack(pady=20)
        
        run_label = ttk.Label(self, text="Run", font=("Helvetica", 14))
        run_label.place(relx=0.3, rely=0.4, anchor=tk.CENTER)
        
        run_button = tk.Button(
            self, 
            text="Start", 
            command=lambda: controller.start_motion_capture("run"), 
            width=30, 
            height=6
        )
        run_button.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
        
        # Will be shown when run is captured
        self.run_captured_label = ttk.Label(self, text="Captured", font=("Helvetica", 14), foreground="gray")
        
        jump_label = ttk.Label(self, text="Jump", font=("Helvetica", 14))
        jump_label.place(relx=0.3, rely=0.7, anchor=tk.CENTER)
        
        jump_button = tk.Button(
            self, 
            text="Start", 
            command=lambda: controller.start_motion_capture("jump"), 
            width=30, 
            height=6
        )
        jump_button.place(relx=0.5, rely=0.7, anchor=tk.CENTER)
        
        # Will be shown when jump is captured
        self.jump_captured_label = ttk.Label(self, text="Captured", font=("Helvetica", 14), foreground="gray")
        
        # Start Game button (initially hidden)
        self.start_game_button = tk.Button(
            self, 
            text="Start Game", 
            command=controller.start_game, 
            width=15, 
            height=3,
            state=tk.DISABLED
        )
        
    def on_show(self):
        """Update the state of the frame when shown"""
        # Show or hide "Captured" labels based on completed motions
        if "run" in self.controller.completed_motions:
            self.run_captured_label.place(relx=0.7, rely=0.4, anchor=tk.CENTER)
        else:
            self.run_captured_label.place_forget()
            
        if "jump" in self.controller.completed_motions:
            self.jump_captured_label.place(relx=0.7, rely=0.7, anchor=tk.CENTER)
        else:
            self.jump_captured_label.place_forget()

        # Show Start Game button when both motions are captured
        if "run" in self.controller.completed_motions and "jump" in self.controller.completed_motions:
            self.start_game_button.config(state=tk.NORMAL)
            self.start_game_button.place(relx=0.5, rely=0.9, anchor=tk.CENTER)
        else:
            # Remove the Start Game button if either motion is not captured
            try:
                self.start_game_button.place_forget()
                self.start_game_button.config(state=tk.DISABLED)
            except:
                pass

class RequestMotionFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.motion_label = ttk.Label(
            self, 
            text="Please create a repeated motion for your character's MOTION",
            font=("Helvetica", 24)
        )
        self.motion_label.pack(pady=20)
        
        button = tk.Button(
            self, 
            text="Start", 
            command=lambda: controller.show_frame("CaptureMotionFrame"), 
            width=40, 
            height=6
        )
        button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    def on_show(self):
        """Update the motion text when shown"""
        motion_type = self.controller.current_motion.upper() if self.controller.current_motion else "MOTION"
        self.motion_label.config(text=f"Please create a repeated motion for your character's {motion_type} motion")

class ErrorMotionFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        
        label1 = ttk.Label(self, text="Error 49", font=("Helvetica", 24))
        label1.pack(pady=20)
        
        label2 = ttk.Label(self, text="Try a different motion,", font=("Helvetica", 24))
        label2.pack(pady=10)
        
        label3 = ttk.Label(self, text="this one was used for another action!", font=("Helvetica", 24))
        label3.pack(pady=10)
        
        button = tk.Button(
            self, 
            text="Start", 
            command=lambda: controller.show_frame("RequestMotionFrame"), 
            width=40, 
            height=6
        )
        button.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

class CaptureMotionFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        label1 = ttk.Label(self, text="Motion captured!", font=("Helvetica", 24))
        label1.pack(pady=20)
        
        label2 = ttk.Label(self, text="Please repeat", font=("Helvetica", 24))
        label2.pack(pady=20)
        
        button = tk.Button(
            self, 
            text="Start", 
            command=lambda: controller.show_frame("SuccessMotionFrame"), 
            width=40, 
            height=6
        )
        button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

class SuccessMotionFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        label = ttk.Label(self, text="Motion capture successful", font=("Helvetica", 24))
        label.pack(pady=20)
        
        button = tk.Button(
            self, 
            text="Back", 
            command=self.complete_and_return, 
            width=40, 
            height=6
        )
        button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    def complete_and_return(self):
        """Mark the current motion as completed and return to the muscle setup frame"""
        self.controller.complete_motion_capture()
        self.controller.show_frame("MuscleSetupFrame")

if __name__ == "__main__":
    app = MotionCaptureApp()
    app.mainloop()
