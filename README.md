# Autonomous Warehouse Inventory & Inspection Robot 🤖📦

[![ROS 2](https://img.shields.io/badge/ROS_2-Humble-3498DB?logo=ros&logoColor=white)](https://docs.ros.org/en/humble/)
[![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white)](https://python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-Perception-5C3EE8?logo=opencv&logoColor=white)](https://opencv.org/)
[![Nav2](https://img.shields.io/badge/Nav2-Autonomous_Navigation-007ACC)](https://navigation.ros.org/)
[![Platform](https://img.shields.io/badge/Hardware-TurtleBot3_Burger-orange)]()

> An autonomous robotic inspection system engineered on **ROS 2 Humble** and a **TurtleBot3 Burger**. Integrates Cartographer SLAM, Nav2 waypoint navigation, real-time HSV color segmentation via OpenCV, and a multi-threaded Tkinter operator dashboard to automate inventory tracking and detect misplaced warehouse stock.

📄 **[Read the Full Technical Report (PDF)](docs/ECTE477_Project_Report.pdf)**

---

## 🏗️ System Architecture & Node Communication

The system is architected into three decoupled sub-systems communicating over custom and standard ROS 2 topics and actions:

```mermaid
flowchart TD
    subgraph Sensing & Base
        A[Raspberry Pi Camera Node] -->|camera/image_raw/compressed| D[Perception Node<br><code>shelf_color_detector.py</code>]
        B[LDS-01 LiDAR / AMCL] -->|/amcl_pose| E[Navigation Coordinator<br><code>motion_control.py</code>]
    end

    subgraph Perception Pipeline
        D -->|HSV Masking & Contours| D1[Bounding Box Extraction]
        D1 -->|/shelf_colors| E
    end

    subgraph Navigation & State Control
        E -->|Action Goal: Pose & Quaternions| F[Nav2 Stack]
        F -->|Cmd_Vel / Motor Actuation| G[TurtleBot3 Base]
        E -->|State, Metrics & Inventory Logs| H[HMI Dashboard<br><code>dashboard.py</code>]
    end

    subgraph Operator UI
        H --> I[Tkinter Live Interface]
    end
