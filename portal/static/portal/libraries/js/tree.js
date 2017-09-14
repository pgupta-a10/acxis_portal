(function() {
	'use strict';
	//angular.module('catalogApp', [ 'ui.tree', 'ui.bootstrap' ]);

	angular.module('catalogApp', [ 'ui.tree', 'ui.bootstrap' ]).config(function($interpolateProvider, $httpProvider) {
	  	$interpolateProvider.startSymbol('{$');
    	$interpolateProvider.endSymbol('$}');

		$httpProvider.defaults.xsrfCookieName = 'csrftoken';
    	$httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
	});

	angular.module('ui.tree').config(function(treeConfig) {
	  treeConfig.defaultCollapsed = true; // collapse nodes by default
	  treeConfig.appendChildOnHover = true; // append dragged nodes as children by default
	});

	angular.module('catalogApp' ).controller(
			'catalogCtrl', ['$scope',  'TreeService', '$modal','$log',
			function($scope,  TreeService, $modal,  $log) {

				$scope.treeOptions = {
				    accept: function(sourceNode, destNodes, destIndex) {

				    	//return true;

				    	var sourceType = sourceNode.$element.attr('data-type');
				        var destType = destNodes.$element.attr('data-type');
				        var destParent = destNodes.$parent;
				        //Product can not be moved under root aka uiTrees
				        if(destParent.$type == 'uiTree' && sourceType==='product') return false;

				        //Category can not be moved under product
				        if(sourceType==='category' && destType==='product' ) return false;

				        return true;
				    },
				    dragMove: function(event) {

				    	$log.info(event);

				    }
				};

				$scope.edit = function(scope) {
					scope.$modelValue.editable = true;
				};

				$scope.update = function(scope, cat) {
					delete cat.editable;
				};

				$scope.delete = function(scope) {
					if (window.confirm('Are you sure to remove node '+ scope.$modelValue.name +'?')) {
						if (window.confirm('Confirming Again! Are you sure to remove node '+ scope.$modelValue.name +'?')) {
							var node_id = scope.$modelValue.id;
							TreeService.delete_node(node_id).then(
							function (response) {
								if(response['success'] == true){
									scope.remove();
								}
							}, function (response) {
							}
						);

						}
					}
				};

				$scope.deleteProduct = function(scope){
					var modelProduct = scope.$modelValue;
					scope.remove();
				};

				$scope.toggle2 = function(scope) {
					//alert(scope.$modelValue.id);
					/*var nodeData = scope.$modelValue;
					nodeData.children.push({
						type: "category",
						id : 2000,
						name : 'test',
						editable : false,
						children : []
					});*/
					var nodeData = scope.$modelValue;
					if (nodeData.children.length > 0){
						scope.toggle();
					}else{
						TreeService.get_children(nodeData.id).then(
							function (response) {
								if (response.length > 0){
									nodeData.children = response;
									scope.toggle();
									scope.toggle();
								}else{
									scope.toggle();
								}
							}, function (response) {
							}
						);
					}
				};

				/*$scope.newSubItem = function(scope) {
					var nodeData = scope.$modelValue;
					alert(nodeData.id);
					nodeData.children.push({
						type: "category",
						parentid: nodeData.id,
						id : nodeData.id * 10 + nodeData.children.length,
						name : nodeData.name + '.'
								+ (nodeData.children.length + 1),
						editable : true,
						children : []
					});
				};*/

				/**
				 * Add New Node (Branch or Leaf node)
				 * @param scope
				 * @param type. If type is "category" - branch node is added else if type is "product" leaf node is added
				 */
				$scope.add_new_node = function(scope, type){
					var parent_modelCat = scope.$modelValue;

				    var modalInstance = $modal.open({
				      templateUrl: '/buginfo/add_node/',
				      controller: 'ProductModalCtrl',
				      resolve: {
				        node: function () {
				          return {"type": type, "children":[], "additional_info":"", "bugs_tracker_ignore": false, "name": null, "release_date":""};
				        },
						node_type: function (){
                            return type;
                        },
						parent_category: function (){
                            return parent_modelCat;
                        },
						operation: function(){return "add"}
				      }
				    });

				    modalInstance.result.then(function (node) {
						TreeService.add_new_node(parent_modelCat.id, node).then(
							function (response) {
								parent_modelCat.children.push(response);
								parent_modelCat.toggle();
							}, function (response) {

							});


				    }, function () {
				      $log.info('Modal dismissed at: ' + new Date());
				    });
				};

				/**
				 * Edit Node
				 * @param scope
				 */
				$scope.edit_node = function(scope){
					var node_obj = scope.$modelValue;
					var modalInstance = $modal.open({
					  templateUrl: '/buginfo/add_node/',
					  controller: 'ProductModalCtrl',
					  resolve: {
						node: function () {
						  return angular.copy(node_obj);
						},
						node_type: function (){
                            return node_obj.type;
                        },
						parent_category: function (){
                            return "";
                        },
						operation: function(){return "edit"}
					  }
					});

					modalInstance.result.then(function (node) {
						TreeService.edit_node(node.id, node).then(
							function (response) {
								scope.$modelValue.additional_info = response.additional_info;
								scope.$modelValue.bugs_tracker_ignore = response.bugs_tracker_ignore;
								scope.$modelValue.release_date = response.release_date;
								scope.$modelValue.name = response.name;
							}, function (response) {

							});

					}, function () {
					  	$log.info('Modal dismissed at: ' + new Date());
					});
				};

				/*$scope.openAddProductModal = function (scope) {
					var modelCat = scope.$modelValue;
				    var modalInstance = $modal.open({
				      templateUrl: '/buginfo/add_node/',
				      controller: 'ProductModalCtrl',
				      resolve: {
				        node: function () {
				          return {"category":modelCat, "type":"product", "parent": modelCat.id};
				        }
				      }
				    });

				    modalInstance.result.then(function (node) {
				    	alert(modelCat.id);
				    	modelCat.children.push(node);
				    }, function () {
				      $log.info('Modal dismissed at: ' + new Date());
				    });
				  };

				  $scope.openEditProductModal = function (scope) {
					  	var modelProduct = scope.$modelValue;

					    var modalInstance = $modal.open({
					      templateUrl: '/buginfo/add_node/',
					      controller: 'ProductModalCtrl',
					      resolve: {
					        node: function () {
					          return angular.copy(modelProduct);
					        }
					      }
					    });

					    modalInstance.result.then(function (node) {

					    	modelProduct.name=node.name;
					    	modelProduct.description=node.description;
					    	modelProduct.sku=node.sku

					    }, function () {
					      $log.info('Modal dismissed at: ' + new Date());
					    });
					  };*/

				/*$scope.catalog = [ {
					"type":"category",
					"id" : 1,
					"name" : "ACOS",
					"children" : [{"type":"product", "id":333, "name":"4.0", "sku":"4.0", "description":"released on MArch 30,2014"}]
				}, {
					"type":"category",
					"id" : 2,
					"name" : "TPS",
					"children" : []
				}, {
					"type":"category",
					"id" : 3,
					"name" : "DCFW",
					"children" : []
				}, {
					"type":"category",
					"id" : 4,
					"name" : "CGN",
					"children" : []
				} ];*/

				var jsonvar = angular.fromJson(my_var);
				$scope.catalog = jsonvar;

				$scope.expand_collapseAll = function(oper){
					var elems = document.getElementsByClassName("angular-ui-tree-node");

					if (oper == "collapse"){
						for(var i=0; i < elems.length; i++){
							angular.element(elems[i]).scope().collapse();
						}
					}else{
						for(var i=0; i < elems.length; i++){
							angular.element(elems[i]).scope().expand();
						}
					}
				};

			}]);

})();


angular.module('catalogApp').controller('ProductModalCtrl', function ($scope, $modalInstance, node, node_type, parent_category, operation) {
		$scope.node = node;
		$scope.parent_category = parent_category;
		$scope.node_type = node_type;
		$scope.operation = operation;


		$scope.save = function () {
			delete $scope.node.category;
			if ($scope.node.name == null || $scope.node.name.trim() ==""){
				alert("Node name is required. Pls. enter a value.");
				return false;
			}

			if ($scope.node.release_date.trim() == ""){
				alert("Release Date is required. Pls. enter a value in mm/dd/yyyy format.");
				return false;
			}
			$modalInstance.close($scope.node);
		};

		$scope.cancel = function () {
			$modalInstance.dismiss('cancel');
		};
	});

