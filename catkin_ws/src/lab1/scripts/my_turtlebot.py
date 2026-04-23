#!/usr/bin/env python3
import rospy
import math
import random
from geometry_msgs.msg import Twist, PoseStamped, Quaternion
from nav_msgs.msg import Odometry
from tf.transformations import euler_from_quaternion

class myTurtle():

    def __init__(self) -> None:
        rospy.init_node('my_turtlebot', anonymous=True)
        self.pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        self.odom_sub = rospy.Subscriber('/odom', Odometry, self.odom_cb)
        self.rate = rospy.Rate(10)
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        rospy.sleep(1.0)
        rospy.loginfo("myTurtle initialized!")

    def odom_cb(self, msg: Odometry) -> None:
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        _, _, self.theta = euler_from_quaternion([q.x, q.y, q.z, q.w])

    def stop(self) -> None:
        self.pub.publish(Twist())
        rospy.sleep(0.5)

    def convert_to_euler(self, quat: Quaternion) -> float:
        _, _, yaw = euler_from_quaternion([quat.x, quat.y, quat.z, quat.w])
        return yaw

    def drive_straight(self, dist: float, vel: float = 0.2) -> None:
        twist = Twist()
        twist.linear.x = vel if dist >= 0 else -vel
        duration = abs(dist) / abs(vel)
        start = rospy.Time.now()
        while (rospy.Time.now() - start).to_sec() < duration and not rospy.is_shutdown():
            self.pub.publish(twist)
            self.rate.sleep()
        self.stop()

    def rotate(self, angle: float) -> None:
        twist = Twist()
        ang_speed = 0.5
        twist.angular.z = ang_speed if angle >= 0 else -ang_speed
        duration = abs(angle) / ang_speed
        start = rospy.Time.now()
        while (rospy.Time.now() - start).to_sec() < duration and not rospy.is_shutdown():
            self.pub.publish(twist)
            self.rate.sleep()
        self.stop()

    def spin_wheels(self, u1: float, u2: float, time: float) -> None:
        # u1 = left wheel, u2 = right wheel
        # linear = avg, angular = diff / wheel_base (0.287m for waffle_pi)
        wheel_base = 0.287
        twist = Twist()
        twist.linear.x  = (u1 + u2) / 2.0
        twist.angular.z = (u2 - u1) / wheel_base
        start = rospy.Time.now()
        while (rospy.Time.now() - start).to_sec() < time and not rospy.is_shutdown():
            self.pub.publish(twist)
            self.rate.sleep()
        self.stop()

    def drive_circle(self, radius: float) -> None:
        linear_speed = 0.2
        twist = Twist()
        twist.linear.x  = linear_speed
        twist.angular.z = linear_speed / radius
        duration = (2 * math.pi * radius) / linear_speed
        start = rospy.Time.now()
        while (rospy.Time.now() - start).to_sec() < duration and not rospy.is_shutdown():
            self.pub.publish(twist)
            self.rate.sleep()
        self.stop()

    def drive_square(self, side: float) -> None:
        for _ in range(4):
            self.drive_straight(side, 0.2)
            rospy.sleep(0.3)
            self.rotate(math.pi / 2)
            rospy.sleep(0.3)

    def nav_to_pose(self, goal: PoseStamped) -> None:
        target_x = goal.pose.position.x
        target_y = goal.pose.position.y
        target_theta = self.convert_to_euler(goal.pose.orientation)

        # Step 1: rotate toward goal
        angle_to_goal = math.atan2(target_y - self.y, target_x - self.x)
        self.rotate(angle_to_goal - self.theta)

        # Step 2: drive straight to goal
        dist = math.sqrt((target_x - self.x)**2 + (target_y - self.y)**2)
        self.drive_straight(dist, 0.2)

        # Step 3: rotate to final orientation
        self.rotate(target_theta - self.theta)

    def random_dance(self) -> None:
        moves = ['straight', 'rotate', 'circle', 'spin']
        for _ in range(8):
            choice = random.choice(moves)
            if choice == 'straight':
                self.drive_straight(random.uniform(0.2, 0.5), 0.2)
            elif choice == 'rotate':
                self.rotate(random.uniform(-math.pi, math.pi))
            elif choice == 'circle':
                self.drive_circle(random.uniform(0.3, 0.6))
            elif choice == 'spin':
                self.spin_wheels(0.1, 0.2, random.uniform(1.0, 2.0))
        self.stop()


def main():
    turtle = myTurtle()

    rospy.loginfo("=== Task 5: Circle r=0.5m ===")
    turtle.drive_circle(0.5)
    rospy.sleep(1.0)

    rospy.loginfo("=== Task 6: Square 0.5m sides ===")
    turtle.drive_square(0.5)
    rospy.sleep(1.0)

    rospy.loginfo("=== Task 8: Random Dance ===")
    turtle.random_dance()


if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass
