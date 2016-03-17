'use strict';
var conn = new WebSocket('ws://localhost:8080');
var App = angular.module("App", []);
var send = function (data) {
  var json = JSON.stringify(data);
  console.log(data);
  console.log(json);
  conn.send(json);
}
App.controller('chatController', function($scope, $http) {
  $scope.logined = false;
  $scope.reg_form = {};
  $scope.login_form = {};
  $scope.messages = [];
  $scope.my_id = 0;
  var url = "/endpoint";
  conn.onopen = function() {
    console.log('Connected');
  };

  var parameter = JSON.stringify({type:"get_user_list"});
  $http.post(url, parameter).
    success(function(data, status, headers, config) {
        $scope.users = data;
        console.log(data);
      }).
      error(function(data, status, headers, config) {
        console.log(data, status, headers, config);
      });


  conn.onmessage = function (e) {
    console.log('onmessage', e.data);
    var data = JSON.parse(e.data)
    if (data.type=='login') {
      $scope.logined = data.logined || false; 
      $scope.login_form = {};
      console.log($scope.logined);
    }
    if (data.type=='register') {
      $scope.logined = data.logined || false; 
      console.log(data.logined);
      $scope.reg_form = {};
    }
    if (data.type=='message') {
      $scope.messages.push(data);
    }
  };

  conn.onclose = function() {
    console.log('Disconnected.');
  };

  $scope.login = function () {
    var msg = {'type':'login'};
    angular.extend(msg, $scope.login_form);
    send(msg);
  };


  $scope.register = function () {
    var msg = {'type':'register'};
    angular.extend(msg, $scope.reg_form);
    send(msg);
  };

  var get_online_user_list = function () {
    var msg = {'type':'get_online_user_list'};
    send(msg);
  }

  $scope.send_message = function () {
    var msg = {'type':'message', 'message': $scope.newMessage.text};
    var d = new Date();
    msg['time'] = d.getTime();
    send(msg);
    $scope.newMessage = {};
  };
});
