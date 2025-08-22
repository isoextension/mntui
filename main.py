#!/opt/mntui/bin/python3
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QMessageBox
import subprocess

class MountGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mount Partition GUI")
        self.resize(350, 180)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Select partition:"))
        self.combo = QComboBox()
        layout.addWidget(self.combo)

        layout.addWidget(QLabel("Mount point (must exist, e.g. /mnt/usb):"))
        self.mount_entry = QLineEdit()
        layout.addWidget(self.mount_entry)

        mount_btn = QPushButton("Mount")
        mount_btn.clicked.connect(self.mount_selected)
        layout.addWidget(mount_btn)

        self.setLayout(layout)

        self.partitions = []
        self.load_partitions()

    def load_partitions(self):
        toprint: list[str] = []

        result = subprocess.run(
            ["lsblk", "-ln", "-o", "NAME,TYPE,MOUNTPOINT,LABEL"],
            capture_output=True,
            text=True
        )

        for line in result.stdout.strip().split("\n"):
            if "[SWAP]" in line:
                continue

            parts = line.split()
            if len(parts) < 2:
                continue  # skip malformed lines

            name = parts[0]
            typ = parts[1]

            # everything after type is mountpoint and label
            mount = ""
            label = ""

            if len(parts) == 2:
                pass  # no mount, no label
            elif len(parts) == 3:
                # could be mount or label
                if parts[2].startswith("/"):
                    mount = parts[2]
                else:
                    label = parts[2]
            else:
                # 4+ fields: first is mountpoint, rest is label
                mount = parts[2] if parts[2].startswith("/") else ""
                label = " ".join(parts[3:]) if len(parts) > 3 else ""

            if typ == "part":
                display_name = name
                if label:
                    display_name += f" ({label})"
                if mount:
                    display_name += f" mounted at {mount}"

                toprint.append(display_name)
                self.combo.addItem(display_name)
                # Store the actual partition data for later use
                self.partitions.append((name, mount))
                index = self.combo.count() - 1
                if mount:
                    self.combo.model().item(index).setEnabled(False)

        return toprint

    def mount_device(self, device, mount_point):
        full_device = f"/dev/{device}"
        try:
            subprocess.run(["pkexec", "mount", full_device, mount_point], check=True)
            print(f"{full_device} mounted at {mount_point} using pkexec")
        except subprocess.CalledProcessError:
            try:
                subprocess.run(["sudo", "mount", full_device, mount_point], check=True)
                print(f"{full_device} mounted at {mount_point} using sudo")
            except subprocess.CalledProcessError:
                print(f"failed to mount {full_device} at {mount_point}")

    def mount_selected(self):
        idx = self.combo.currentIndex()
        device, mount = self.partitions[idx]
        if mount:
            QMessageBox.warning(self, "Error", "selected partition is already mounted")
            return

        mount_point = self.mount_entry.text().strip()
        if not mount_point:
            QMessageBox.warning(self, "Error", "please enter a mount point")
            return

        self.mount_device(device, mount_point)
        QMessageBox.information(self, "Success", f"/dev/{device} mounted at {mount_point}")

def mount_from_args():
    if len(sys.argv) < 3:
        print("Usage: python mount_gui.py <partition_name> <mount_point>")
        sys.exit(1)
    device = sys.argv[1]
    mount_point = sys.argv[2]
    full_device = f"/dev/{device}"
    try:
        subprocess.run(["pkexec", "mount", full_device, mount_point], check=True)
        print(f"{full_device} mounted at {mount_point} using pkexec")
    except subprocess.CalledProcessError:
        try:
            subprocess.run(["sudo", "mount", full_device, mount_point], check=True)
            print(f"{full_device} mounted at {mount_point} using sudo")
        except subprocess.CalledProcessError:
            print(f"failed to mount {full_device} at {mount_point}")
    sys.exit(0)

if __name__ == "__main__":
    # if args given, mount immediately and exit
    if len(sys.argv) >= 3:
        mount_from_args()

    app = QApplication(sys.argv)
    window = MountGUI()
    window.show()
    sys.exit(app.exec())
