
 /*!
  * Copyright 2017,  Digital Reasoning
  * 
  * Licensed under the Apache License, Version 2.0 (the "License");
  * you may not use this file except in compliance with the License.
  * You may obtain a copy of the License at
  * 
  *     http://www.apache.org/licenses/LICENSE-2.0
  * 
  * Unless required by applicable law or agreed to in writing, software
  * distributed under the License is distributed on an "AS IS" BASIS,
  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  * See the License for the specific language governing permissions and
  * limitations under the License.
  * 
*/

define([
    'generics/permissions'
], function(MPBase) {
    'use strict';
    return MPBase.extend({
        permsUrl: '/api/environments/' + window.stackdio.objectId + '/permissions/',
        saveUrl: '/environments/' + window.stackdio.objectId + '/',
        init: function () {
            this._super();

            this.breadcrumbs = [
                {
                    active: false,
                    title: 'Environments',
                    href: '/environments/'
                },
                {
                    active: false,
                    title: window.stackdio.environmentName,
                    href: this.saveUrl
                },
                {
                    active: true,
                    title: 'Permissions'
                }
            ];
        }
    });
});