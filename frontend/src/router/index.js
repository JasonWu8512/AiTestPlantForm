import { createRouter, createWebHistory } from "vue-router";

import MainLayout from "../components/layout/MainLayout.vue";
import DashboardView from "../views/dashboard/DashboardView.vue";
import LoginView from "../views/login/LoginView.vue";
import ExecutionsView from "../views/executions/ExecutionsView.vue";
import NotificationsView from "../views/notifications/NotificationsView.vue";
import ProjectsView from "../views/projects/ProjectsView.vue";
import ReportsView from "../views/reports/ReportsView.vue";
import TestCasesView from "../views/testcases/TestCasesView.vue";
import TestPlansView from "../views/testplans/TestPlansView.vue";
import UsersView from "../views/users/UsersView.vue";
import { useAuthStore } from "../stores/auth";


const routes = [
  {
    path: "/login",
    name: "login",
    component: LoginView
  },
  {
    path: "/",
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: "",
        name: "dashboard",
        component: DashboardView
      },
      {
        path: "users",
        name: "users",
        component: UsersView
      },
      {
        path: "projects",
        name: "projects",
        component: ProjectsView
      },
      {
        path: "testcases",
        name: "testcases",
        component: TestCasesView
      },
      {
        path: "testplans",
        name: "testplans",
        component: TestPlansView
      },
      {
        path: "executions",
        name: "executions",
        component: ExecutionsView
      },
      {
        path: "reports",
        name: "reports",
        component: ReportsView
      },
      {
        path: "notifications",
        name: "notifications",
        component: NotificationsView
      }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to) => {
  const authStore = useAuthStore();
  if (to.meta.requiresAuth && !authStore.accessToken) {
    return { name: "login" };
  }
  if (to.name === "login" && authStore.accessToken) {
    return { name: "dashboard" };
  }
  return true;
});

export default router;
