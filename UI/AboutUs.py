from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class AboutUs(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        title = QLabel("ABOUT US – SMART RETAIL")
        title.setFont(QFont())
        title.setStyleSheet("""
            color: #b3475f;
            margin-top: 10px;
            font: 30pt "MS Shell Dlg 2"; 
            font-weight: bold;   
        """)

        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        intro = QLabel(
            "Smart Retail is a seasonal product recommendation and market-insight platform designed to help businesses accurately predict\n"
            "and capture customer demand throughout the year.\n"
            "We provide fast, simple, and actionable insights, enabling companies to optimize their strategies, align offerings with seasonal trends, \n"
            "and make smarter business decisions without spending excessive time on analysis."
        )
        intro.setFont(QFont("MS Shell Dlg 2", 13))
        intro.setWordWrap(True)
        intro.setStyleSheet("padding: 10px;font: 13pt")
        layout.addWidget(intro)

        missionTitle = QLabel("Our Mission")
        missionTitle.setFont(QFont("MS Shell Dlg 2", 18, QFont.Weight.Bold))
        missionTitle.setStyleSheet("color: #b3475f; margin-top: 15px;font: 18pt;font-weight: bold;")
        layout.addWidget(missionTitle)

        mission = QLabel(
            "- Deliver smart and data-driven market insights for seasonal demand.\n"
            "- Help businesses understand what customers need in each season or period.\n"
            "- Provide actionable recommendations that optimize decision-making and reduce unnecessary operational costs."
        )
        mission.setFont(QFont("S Shell Dlg 2", 13))
        mission.setWordWrap(True)
        layout.addWidget(mission)

        visionTitle = QLabel("Our Vision")
        visionTitle.setFont(QFont("MS Shell Dlg 2", 16, QFont.Weight.Bold))
        visionTitle.setStyleSheet("color: #b3475f; margin-top: 15px;font: 18pt;font-weight: bold;")
        layout.addWidget(visionTitle)

        vision = QLabel(
            "- Become a trusted seasonal demand-insight platform for businesses.\n"
            "- Continuously update market and consumer trends to enhance strategic decision-making.\n"
            "- Provide a modern, intuitive, and efficient experience that supports businesses in understanding and responding to customer needs."
        )
        vision.setFont(QFont("MS Shell Dlg 2", 13))
        vision.setWordWrap(True)
        layout.addWidget(vision)

        coreTitle = QLabel("Core Values")
        coreTitle.setFont(QFont("MS Shell Dlg 2", 18, QFont.Weight.Bold))
        coreTitle.setStyleSheet("color: #b3475f; margin-top: 20px;font: 18pt;font-weight: bold;")
        layout.addWidget(coreTitle)

        row = QHBoxLayout()

        row.addWidget(self.createCard(
            "Accuracy",
            "Deliver precise and data-driven seasonal demand insights.",
            "#ffe6ec", "#d17a8b"      # pink theme
        ))

        row.addWidget(self.createCard(
            "Speed",
            "Fast and actionable market recommendations.",
            "#f3e8ff", "#b38cd9"      # pastel purple
        ))

        row.addWidget(self.createCard(
            "Usability",
            "Simple, intuitive, and decision-support-oriented interface.",
            "#e8faff", "#7bb8c9"      # pastel blue
        ))

        row.addWidget(self.createCard(
            "Security",
            "Secure and trusted data management.",
            "#fff5d9", "#d9b97a"      # pastel yellow
        ))

        layout.addLayout(row)
        self.setLayout(layout)

    def createCard(self, title, description, bgColor, borderColor):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {bgColor};
                border: 2px solid {borderColor};
                border-radius: 12px;
                padding: 12px;
            }}
        """)

        vbox = QVBoxLayout()

        lblTitle = QLabel(title)
        lblTitle.setFont(QFont("MS Shell Dlg 2", 16, QFont.Weight.Bold))
        lblTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lblTitle.setStyleSheet("""      
            color: rgb(104, 83, 92);  
            font: 18pt;
            font-weight: bold;
        """)

        lblDesc = QLabel(description)
        lblDesc.setFont(QFont("MS Shell Dlg 2", 13))
        lblDesc.setStyleSheet("""     
                   color: rgb(104, 83, 92);  
                   font: 13pt;
               """)
        lblDesc.setWordWrap(True)
        lblDesc.setAlignment(Qt.AlignmentFlag.AlignCenter)

        vbox.addWidget(lblTitle)
        vbox.addWidget(lblDesc)
        frame.setLayout(vbox)

        return frame
