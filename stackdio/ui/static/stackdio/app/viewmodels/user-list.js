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
    'jquery',
    'generics/pagination',
    'models/user'
], function ($, Pagination, User) {
    'use strict';

    return Pagination.extend({
        breadcrumbs: [
            {
                active: true,
                title: 'Users'
            }
        ],
        model: User,
        baseUrl: '/users/',
        initialUrl: '/api/users/',
        detailRequiresAdvanced: true,
        sortableFields: [
            {name: 'username', displayName: 'Username', width: '25%'},
            {name: 'firstName', displayName: 'First Name', width: '20%'},
            {name: 'lastName', displayName: 'Last Name', width: '20%'},
            {name: 'email', displayName: 'Email', width: '35%'}
        ]
    });
});
