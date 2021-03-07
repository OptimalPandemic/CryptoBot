<template>
  <div id="app" class="container-fluid">
    <div class="row">
      <Navbar></Navbar>
      <Sidebar></Sidebar>
      <router-view/>
    </div>
  </div>
</template>

<script>
import Navbar from '@/components/Navbar'
import Sidebar from '@/components/Sidebar'

export default {
  name: 'App',
  components: {
    Navbar,
    Sidebar
  },
  methods: {
    logout() {

    }
  }
}
</script>

<style>

</style>
