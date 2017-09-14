'use strict';

/**
 * @ngdoc service
 * @name qadashboardApp.releaseFactory
 * @description
 * # releaseFactory
 * Factory in the qadashboardApp.
 */
var module = angular.module('catalogApp');

    var path = "http://127.0.0.1:8000" + '/buginfo/api/';

    module.factory('TreeService',[
        '$q',
        '$http',
        function ($q, $http) {

        var TreeService  ={

            getQAReleaseInfo: function(releaseId){
                var endpoint = path + releaseId + '/releaseinfo';
                var deferred = $q.defer();
				var promise = deferred.promise;
                var request = $http.get(endpoint, {xsrfCookieName:'csrftoken', responseType:'json',withCredentials: true});
                request.success(function(data){
                    deferred.resolve(data);
                });
                 request.error(function (data, status, headers, config) {
                     deferred.reject(data,status);
                 });
                return promise;
            },
            add_new_node:function(parent_id, node){
                var endpoint = path + parent_id + '/add';
                var deferred = $q.defer();
				var promise = deferred.promise;
                var request = $http.post(endpoint, node, {xsrfCookieName:'csrftoken', responseType:'json',withCredentials: false});
                request.success(function(data){
                    deferred.resolve(data);
                });
                 request.error(function (data, status, headers, config) {
                     deferred.reject(data,status);
                 });
                 return promise;
            },
            edit_node:function(node_id, node){
                var endpoint = path + node_id + '/edit';
                var deferred = $q.defer();
				var promise = deferred.promise;
                var request = $http.post(endpoint, node, {xsrfCookieName:'csrftoken', responseType:'json',withCredentials: false});
                request.success(function(data){
                    deferred.resolve(data);
                });
                 request.error(function (data, status, headers, config) {
                     deferred.reject(data,status);
                 });
                 return promise;
            },
             delete_node:function(node_id){
                var endpoint = path + node_id + '/delete';
                var deferred = $q.defer();
				var promise = deferred.promise;
                var request = $http.post(endpoint, {xsrfCookieName:'csrftoken', responseType:'json',withCredentials: false});
                request.success(function(data){
                    deferred.resolve(data);
                });
                 request.error(function (data, status, headers, config) {
                     deferred.reject(data,status);
                 });
                 return promise;
            },
            get_children:function(node_id){
                var endpoint = path + node_id + '/children';
                var deferred = $q.defer();
				var promise = deferred.promise;
                var request = $http.get(endpoint, {xsrfCookieName:'csrftoken', responseType:'json',withCredentials: false});
                request.success(function(data){
                    deferred.resolve(data);
                });
                 request.error(function (data, status, headers, config) {
                     deferred.reject(data,status);
                 });
                 return promise;
            }

        };
         return TreeService;
  }]);
