<template>
    <nav id="sidebarMenu" class="col-md-3 col-lg-2 d-md-block bg-light sidebar collapse">
        <div class="position-sticky pt-3">
            <ul class="nav flex-column">
                <li class="nav-item">
                <a class="nav-link active" aria-current="page" href="#">
                    <span data-feather="home"></span>
                    Dashboard
                </a>
                </li>
                <li class="nav-item">
                <a class="nav-link" href="#">
                    <span data-feather="activity"></span>
                    Orders
                </a>
                </li>
                <li class="nav-item">
                <a class="nav-link" href="#">
                    <span data-feather="dollar-sign"></span>
                    Portfolio
                </a>
                </li>
                <li class="nav-item">
                <a class="nav-link" href="#">
                    <span data-feather="trending-up"></span>
                    Reports
                </a>
                </li>
                <li class="nav-item">
                <a class="nav-link" href="#">
                    <span data-feather="sliders"></span>
                    Settings
                </a>
                </li>
            </ul>
        </div>
    </nav>
</template>
<script>
export default {
    name: 'Sidebar'
}
</script>
<style>

</style>
