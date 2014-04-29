/* jshint camelcase: false */

var App, NPMap;

App = {
  handleModuleCloseClick: function() {
    NPMap.app.toggleModule('info', false);
  },
  handleModuleTabClick: function(el) {
    NPMap.app.toggleModule(el.id.replace('module-tab-', ''), true);
  },
  toggleModule: function(module, on) {
    var $module = $('#module-' + module),
    $modules = $('#modules');

    if (on) {
      $('#modules-tabs').hide();
      $module.show();
      $modules.show();
      $('#center').css({
        left: $module.outerWidth() + 'px'
      });
    } else {
      $modules.hide();
      $('#center').css({
        left: '0'
      });
      $module.hide();
      $('#modules-tabs').show();
    }
  }
};

NPMap = {
  baseLayers: ['mapbox-terrain'],
  center: {
    lat: 35.600649300000000000,
    lng: -83.508774500000010000
  },
  div: 'map',
  fullscreenControl: true,
  homeControl: {
    position: 'topright'
  },
  hooks: {
    init: function(callback) {
      document.getElementById('my-custom-module').innerHTML = '' +
    '<p>Search for a date or tag<br> (i.e. April 12, 2014 or amenity)</p>' +
    '<div id="unit-list">' +
      '<input type="text" class="fuzzy-search" placeholder="Search">' +
      '<button class="sort" data-sort="date">Search</button>' +
      '<ul class="list">' +
      '<li><a href="../data/reports/osm_change_report_04-28-14">April 11, 2014</h3></li>' +
      '<li><h3>April 12, 2014</h3></li>' +
      '<li><h3>April 13, 2014</h3></li>' +
      '<li><h3>April 14, 2014</h3></li>' +
      '<li><h3>April 15, 2014</h3></li>' +
      '<li><h3>April 16, 2014</h3></li>' +
      '<ul>' +
    '</div>' +
  '';
    callback();
    }
  },
  modules: [{
    content: '<div id="my-custom-module"></div>',
    icon: 'info',
    title: 'OSM Edits by Date',
    type: 'custom',
    visible: false
  }],
  overlays: [{
    type: 'geojson',
    style: {
      'color': '#ff7800',
      'weight': 5,
      'opacity': 0.65
    },
    url: 'https://raw.githubusercontent.com/nationalparkservice/data/gh-pages/base_data/boundaries/parks/grsm.geojson',
  }],
  printControl: true,
  shareControl: true,
  smallzoomControl: {
    position: 'topright'
  },
  zoom: 10
};

(function() {
  var s = document.createElement('script');
  s.src = 'http://www.nps.gov/npmap/npmap.js/latest/npmap-bootstrap.min.js';
  document.body.appendChild(s);
})();